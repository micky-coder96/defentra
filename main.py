import os
import joblib
from typing import List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Security, Defense, SIEM, Threat Intelligence, and Notifications modules
from waf_rules import detect_sql_injection, detect_xss
from Active_defense import block_malicious_ip
from models_db import init_db, SessionLocal, SecurityEventModel
from threat_intel import enrich_ip_address
from notifications import send_security_alert
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize FastAPI application
app = FastAPI(
    title="Defentra Enterprise SIEM, Threat Intel & Webhook API", version="6.0"
)

# --- Initialize Permanent SIEM Database ---
init_db()


# --- Helper Function for SIEM Database Logging & Webhook Notifications ---
def log_siem_event(
    event_type: str,
    source_ip: str,
    severity: str,
    description: str,
    confidence: float = None,
):
    db = SessionLocal()
    try:
        event = SecurityEventModel(
            event_type=event_type,
            source_ip=source_ip,
            severity=severity,
            description=description,
            confidence=confidence,
        )
        db.add(event)
        db.commit()

        # Automatically push webhook notification for High or Critical threats
        if severity in ["Critical", "High"]:
            send_security_alert(event_type, source_ip, severity, description)

    finally:
        db.close()


# --- Rate Limiter Setup ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- WAF & Active IPS Middleware (SQLi, XSS, Auto-Blocking & SIEM Logging) ---
@app.middleware("http")
async def waf_security_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    query_string = str(request.url.query)

    body_content = ""
    if request.method in ["POST", "PUT"]:
        try:
            body_bytes = await request.body()
            body_content = body_bytes.decode("utf-8", errors="ignore")
        except Exception:
            body_content = ""

    combined_payload = query_string + " " + body_content

    # Inspect for SQL Injection
    if detect_sql_injection(combined_payload):
        print(f"[WAF SECURITY ALERT] SQL Injection detected from IP: {client_ip}")
        block_malicious_ip(client_ip)  # Active Defense OS Firewall Block
        log_siem_event(
            event_type="WAF_SQLI_BLOCK",
            source_ip=client_ip,
            severity="Critical",
            description="Blocked SQL Injection attempt and triggered firewall ban.",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Potential SQL Injection attack detected. Your IP has been blocked.",
        )

    # Inspect for Cross-Site Scripting (XSS)
    if detect_xss(combined_payload):
        print(f"[WAF SECURITY ALERT] XSS attempt detected from IP: {client_ip}")
        block_malicious_ip(client_ip)  # Active Defense OS Firewall Block
        log_siem_event(
            event_type="WAF_XSS_BLOCK",
            source_ip=client_ip,
            severity="High",
            description="Blocked Cross-Site Scripting (XSS) attempt and triggered firewall ban.",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Potential Cross-Site Scripting (XSS) attack detected. Your IP has been blocked.",
        )

    response = await call_next(request)
    return response


# --- Load Machine Learning Intrusion Model ---
MODEL_PATH = "models/defentra_rf_model.pkl"
ENCODER_PATH = "models/protocol_encoder.pkl"

if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    print("[*] Loading Defentra ML Model into memory...")
    ml_model = joblib.load(MODEL_PATH)
    protocol_encoder = joblib.load(ENCODER_PATH)
else:
    print("[-] Warning: ML Model files not found. Run train_model.py first!")
    ml_model = None
    protocol_encoder = None


# --- Schemas ---
class NetworkAlert(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str
    packet_size: int
    prediction: str
    confidence_score: float


class EmailAlert(BaseModel):
    sender: str
    subject: str
    body_snippet: str
    prediction: str
    confidence_score: float
    contains_suspicious_url: bool


# --- Root & Test Endpoints ---
@app.get("/")
def read_root():
    return {
        "status": "Online",
        "platform": "Defentra Security Operations Center Core Engine",
    }


@app.get("/api/search")
def search_database(q: str = ""):
    """Search endpoint protected by the WAF middleware."""
    return {"results": f"Successfully searched for query: {q}"}


# --- Network Endpoints ---
@app.post("/api/network-alert")
def receive_network_alert(alert: NetworkAlert):
    severity = "High" if alert.prediction == "Attack" else "Low"
    log_siem_event(
        event_type="ML_NETWORK_SCAN",
        source_ip=alert.source_ip,
        severity=severity,
        description=f"Packet classification: {alert.prediction} ({alert.protocol})",
        confidence=alert.confidence_score,
    )
    return {"status": "success", "message": "Network alert logged to SIEM."}


# --- Email Endpoints ---
@app.post("/api/email-alert")
def receive_email_alert(alert: EmailAlert):
    severity = "Critical" if alert.prediction == "Phishing" else "Medium"
    log_siem_event(
        event_type="PHISHING_DETECTION",
        source_ip=alert.sender,
        severity=severity,
        description=f"Email flagged as {alert.prediction} with subject: {alert.subject}",
        confidence=alert.confidence_score,
    )
    print(
        f"[EMAIL API] Captured threat from: {alert.sender} -> Marked as: {alert.prediction}"
    )
    return {"status": "success", "message": "Email alert logged to SIEM."}


# --- SIEM Audit Trail Endpoint ---
@app.get("/api/siem/audit-logs", response_model=List[dict])
def get_siem_audit_logs():
    db = SessionLocal()
    try:
        events = (
            db.query(SecurityEventModel)
            .order_by(SecurityEventModel.timestamp.desc())
            .all()
        )
        return [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "source_ip": e.source_ip,
                "severity": e.severity,
                "description": e.description,
                "confidence": e.confidence,
            }
            for e in events
        ]
    finally:
        db.close()


# --- Threat Intelligence & Geolocation Endpoint ---
@app.get("/api/siem/enrich-ip/{ip_address}")
def get_ip_intel(ip_address: str):
    intel_data = enrich_ip_address(ip_address)
    return {"status": "success", "threat_intelligence": intel_data}


# --- Rate-Limited Endpoint ---
@app.post("/api/secure-login")
@limiter.limit("5/minute")
def secure_login(request: Request):
    return {"status": "success", "message": "Login request evaluated securely."}
