# 🛡️ Defentra — AI-Powered Cybersecurity Threat Detection & Active Defense Platform

> **Defentra** is an AI-assisted cybersecurity platform designed to detect, analyze, log, and actively respond to multiple types of cyber threats through a unified security architecture.

Defentra combines **Machine Learning-based network threat detection, Web Application Firewall (WAF), SQL Injection and XSS protection, rate limiting, automated IP blocking, SIEM-based security logging, IP geolocation/threat intelligence, phishing detection, real-time webhook notifications, and a unified SOC dashboard** into a single platform.

The goal is to move beyond passive threat monitoring toward an **automated detection, analysis, and response system**.

---

## 🚀 Key Features

### 1. 🤖 Machine Learning Network Threat Detection

Defentra integrates a trained Machine Learning model for analyzing network/packet classification data.

The system can receive network security information such as:

* Source IP
* Destination IP
* Network protocol
* Packet size
* ML prediction
* Confidence score

The prediction is then converted into a security event and stored in the SIEM system.

**Example classifications:**

```text
Normal Traffic
Attack / Suspicious Traffic
```

The project uses a serialized Random Forest model and protocol encoder:

```text
models/
├── defentra_rf_model.pkl
└── protocol_encoder.pkl
```

---

### 2. 🔥 Web Application Firewall (WAF)

Defentra includes a custom WAF middleware that inspects incoming HTTP requests before they reach the application.

The WAF analyzes:

* Query parameters
* Request bodies
* HTTP requests
* Suspicious payload patterns

It currently provides protection against:

* SQL Injection (SQLi)
* Cross-Site Scripting (XSS)

When a malicious payload is detected, the request is rejected.

```text
Incoming Request
       ↓
     WAF
       ↓
 ┌─────┴─────┐
 │           │
Safe       Malicious
 │           │
 ↓           ↓
App      Block Request
            ↓
       Active Defense
            ↓
         SIEM Log
```

The WAF and active defense modules are integrated directly into the FastAPI middleware.

---

### 3. 🛡️ Active Defense / IPS

Unlike a traditional monitoring-only IDS, Defentra can take an active response when a malicious request is detected.

For detected attacks, the platform can:

1. Identify the source IP.
2. Classify the security event.
3. Trigger the active defense module.
4. Create a Windows Firewall blocking rule.
5. Record the event in the SIEM database.

This allows Defentra to move from:

```text
Detect → Alert
```

to:

```text
Detect → Analyze → Block → Log → Alert
```

The active defense mechanism uses operating-system firewall controls and therefore requires administrator privileges during execution.

---

### 4. 🚦 Rate Limiting & Brute-Force Protection

Defentra uses **SlowAPI** to limit repeated requests to sensitive endpoints.

For example:

```text
/api/secure-login
```

is configured with:

```text
5 requests / minute
```

This helps protect against:

* Brute-force attacks
* Excessive login attempts
* Request flooding
* Basic automated abuse

---

### 5. 🗄️ SIEM — Security Information and Event Management

Defentra contains a persistent SIEM layer that centralizes security events from different detection modules.

Instead of keeping alerts only in temporary memory, security events are stored permanently using:

```text
SQLite
+
SQLAlchemy ORM
```

The SIEM stores information such as:

* Event ID
* Timestamp
* Event type
* Source IP
* Severity
* Description
* ML confidence score

Example:

```json
{
  "event_type": "WAF_SQLI_BLOCK",
  "source_ip": "127.0.0.1",
  "severity": "Critical",
  "description": "Blocked SQL Injection attempt and triggered firewall ban."
}
```

The project successfully records security events with timestamps and severity levels in the SQLite database.

Database:

```text
defentra_siem.db
```

---

### 6. 🌍 Threat Intelligence & IP Geolocation

Defentra can enrich IP addresses with additional contextual information.

The threat intelligence module can retrieve:

* IP address
* Country
* City
* Region
* ISP

Private/local addresses are handled separately instead of being sent for external lookup.

Example API:

```text
GET /api/siem/enrich-ip/{ip_address}
```

Example:

```text
/api/siem/enrich-ip/8.8.8.8
```

This allows the SOC dashboard to provide additional context about the origin of suspicious traffic.

The documented implementation uses Python `requests` with an IP geolocation service.

---

### 7. 📧 Phishing / Email Threat Detection

Defentra provides an API endpoint for receiving email security classifications.

The system can process:

* Sender
* Subject
* Body snippet
* Prediction
* Confidence score
* Suspicious URL indicator

Example classification:

```text
Phishing
Legitimate / Safe
```

Phishing events are also forwarded into the centralized SIEM logging system.

API:

```text
POST /api/email-alert
```

---

### 8. 🔔 Real-Time Security Notifications

Defentra can send real-time security notifications to team communication channels using webhooks.

Supported integration architecture includes:

* Discord
* Slack

High-severity events can trigger notifications containing:

```text
Event
Severity
Source IP
Description
```

Example:

```text
🚨 DEFENTRA SECURITY ALERT 🚨

Event: WAF_SQLI_BLOCK
Severity: Critical
Source IP: 192.168.x.x
Description: SQL Injection attempt blocked
```

The documented implementation triggers webhook notifications for **High** and **Critical** events.

---

### 9. 🖥️ Unified SOC Dashboard

Defentra includes a browser-based Security Operations Center dashboard built using:

* HTML5
* JavaScript
* Tailwind CSS
* Fetch API

The dashboard provides a centralized view of security activity.

It can display:

* Total security events
* Critical events
* Security event types
* Source IP addresses
* Event severity
* Event descriptions
* SIEM audit logs
* Backend connection status

The dashboard automatically refreshes SIEM data every **5 seconds**.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │    Incoming Traffic │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │        WAF          │
                         │   SQLi / XSS Scan   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                      Safe Request        Malicious
                         │                     │
                         ▼                     ▼
                  Application          Active Defense
                                               │
                                               ▼
                                      Windows Firewall
                                               │
                         ┌─────────────────────┴───────────────┐
                         │                                     │
                         ▼                                     ▼
                  SIEM Database                       Webhook Alert
                         │                              Discord/Slack
                         ▼
                ┌───────────────────┐
                │ Threat Intelligence│
                │   IP Geolocation   │
                └─────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   SOC Dashboard  │
                 └──────────────────┘


       Network Traffic
              │
              ▼
       ML Packet Classifier
              │
              ▼
       Attack / Normal
              │
              ▼
             SIEM


       Email
         │
         ▼
   Phishing Detection
         │
         ▼
        SIEM
         │
         ▼
   Webhook / Dashboard
```

---

# 🧩 Technology Stack

| Layer                | Technology                  |
| -------------------- | --------------------------- |
| Programming Language | Python                      |
| Backend Framework    | FastAPI                     |
| ASGI Server          | Uvicorn                     |
| Machine Learning     | Scikit-learn                |
| ML Model             | Random Forest               |
| Model Serialization  | Joblib                      |
| Database             | SQLite                      |
| ORM                  | SQLAlchemy                  |
| Rate Limiting        | SlowAPI                     |
| Request Validation   | Pydantic                    |
| HTTP Client          | Requests                    |
| Security Layer       | Custom WAF                  |
| Active Defense       | Windows Firewall Automation |
| Frontend             | HTML5                       |
| Styling              | Tailwind CSS                |
| Frontend Logic       | JavaScript                  |
| API Communication    | Fetch API                   |
| Security Monitoring  | SIEM                        |
| Notifications        | Discord / Slack Webhooks    |

The documented project stack specifically identifies Python/FastAPI/Uvicorn, SQLite/SQLAlchemy, custom WAF patterns, SlowAPI, Windows Firewall automation, HTML5, Tailwind CSS, and JavaScript.

---

# 📁 Project Structure

A recommended structure based on the implemented modules:

```text
Defentra/
│
├── main.py
│
├── waf_rules.py
├── active_defense.py
├── models_db.py
├── threat_intel.py
├── notifications.py
│
├── train_model.py
├── test_waf_attack.py
│
├── dashboard.html
│
├── defentra_siem.db
│
├── models/
│   ├── defentra_rf_model.pkl
│   └── protocol_encoder.pkl
│
├── venv/
│
└── README.md
```

### Module Responsibilities

| File                 | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `main.py`            | Main FastAPI application and API integration |
| `waf_rules.py`       | SQL Injection and XSS detection              |
| `active_defense.py`  | Automated malicious IP blocking              |
| `models_db.py`       | SQLAlchemy SIEM database models              |
| `threat_intel.py`    | IP geolocation and threat enrichment         |
| `notifications.py`   | Discord/Slack webhook notifications          |
| `train_model.py`     | Machine Learning model training              |
| `test_waf_attack.py` | Security attack simulation/testing           |
| `dashboard.html`     | SOC monitoring dashboard                     |
| `defentra_siem.db`   | Persistent security event database           |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Defentra.git
cd Defentra
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\activate
```

The project documentation uses a Python virtual environment before installing the required packages.

---

## 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy requests slowapi joblib scikit-learn numpy pydantic
```

---

# 🔐 Configuration

## Machine Learning Model

Make sure the trained model files exist:

```text
models/
├── defentra_rf_model.pkl
└── protocol_encoder.pkl
```

If the files are missing, train the model using:

```bash
python train_model.py
```

---

## Webhook Configuration

Open:

```text
notifications.py
```

Configure your Discord or Slack webhook:

```python
WEBHOOK_URL = "YOUR_WEBHOOK_URL"
```

**Do not commit private webhook URLs or API keys to GitHub.**

For a public repository, environment variables should be used instead.

---

# ▶️ Running Defentra

## Step 1 — Start the Backend

Because Active Defense modifies Windows Firewall rules, run the backend with **Administrator privileges**.

```powershell
.\venv\Scripts\activate
uvicorn main:app --reload
```

The FastAPI server will run on:

```text
http://localhost:8000
```

The documented setup requires administrator privileges because the active defense component modifies local firewall rules.

---

# 🖥️ Launch the SOC Dashboard

Open:

```text
dashboard.html
```

in:

* Chrome
* Microsoft Edge
* Firefox

The dashboard communicates with the FastAPI backend and periodically retrieves SIEM events.

It provides a centralized security monitoring interface.

---

# 🧪 Security Testing

Open another terminal:

```powershell
.\venv\Scripts\activate
python test_waf_attack.py
```

The test suite is designed to simulate security scenarios including:

```text
SQL Injection
XSS
Rate Limiting / Brute Force
```

The documented testing workflow starts the FastAPI server first and then executes `test_waf_attack.py`.

---

# 🔌 API Endpoints

| Method | Endpoint                           | Purpose                                  |
| ------ | ---------------------------------- | ---------------------------------------- |
| `GET`  | `/api/siem/audit-logs`             | Retrieve historical SIEM security events |
| `GET`  | `/api/siem/enrich-ip/{ip_address}` | IP geolocation/threat intelligence       |
| `POST` | `/api/network-alert`               | Receive ML network classification alerts |
| `POST` | `/api/email-alert`                 | Receive phishing/email security alerts   |
| `POST` | `/api/secure-login`                | Rate-limited login security test         |

These endpoints are part of the documented Defentra API architecture.

---

# 📊 SIEM Audit Logs

You can access the security audit trail through:

```text
http://localhost:8000/api/siem/audit-logs
```

Example response:

```json
[
  {
    "id": 4,
    "timestamp": "2026-08-13T10:27:49",
    "event_type": "WAF_SQLI_BLOCK",
    "source_ip": "127.0.0.1",
    "severity": "Critical",
    "description": "Blocked SQL Injection attempt and triggered firewall ban.",
    "confidence": null
  }
]
```

Security events are permanently stored in:

```text
defentra_siem.db
```

---

# 🌍 IP Threat Intelligence

To enrich an IP address:

```text
GET /api/siem/enrich-ip/{ip_address}
```

Example:

```text
http://localhost:8000/api/siem/enrich-ip/8.8.8.8
```

The response can contain:

```json
{
  "ip": "8.8.8.8",
  "country": "United States",
  "city": "Mountain View",
  "isp": "..."
}
```

---

# 🔄 How Defentra Works

### Normal Request

```text
User Request
     ↓
FastAPI
     ↓
WAF Inspection
     ↓
Safe
     ↓
Application
```

### SQL Injection Attack

```text
Malicious Request
       ↓
      WAF
       ↓
SQL Injection Detected
       ↓
 Request Blocked
       ↓
 Active IP Defense
       ↓
Windows Firewall
       ↓
 SIEM Database
       ↓
Webhook Alert
       ↓
SOC Dashboard
```

### Network Threat

```text
Network Packet
      ↓
ML Classifier
      ↓
Prediction + Confidence
      ↓
Security Event
      ↓
SIEM
      ↓
Dashboard / Alert
```

### Phishing Email

```text
Email
  ↓
Email Detection
  ↓
Phishing Classification
  ↓
Confidence Score
  ↓
SIEM
  ↓
Webhook
  ↓
SOC Dashboard
```

---

# 🎯 Use Cases

Defentra can be used as a security monitoring and defensive platform for:

* Web application security monitoring
* SQL Injection detection
* XSS detection
* Suspicious network traffic classification
* Phishing detection
* Brute-force protection
* Automated malicious IP blocking
* Security event logging
* Security operations monitoring
* IP geolocation analysis
* Real-time security notifications
* Cybersecurity experimentation and education

---

# 💡 Why Defentra?

Traditional security tools often operate as separate components:

```text
WAF
 ↓
Network Monitor
 ↓
SIEM
 ↓
Firewall
 ↓
Alert System
```

Defentra attempts to connect these components into a unified workflow:

```text
              ┌───────────────┐
              │ Threat Source │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    Detect     │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    Analyze    │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    Respond    │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │      Log      │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    Notify     │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    Monitor    │
              └───────────────┘
```

This architecture gives the project both **detection and response capabilities** rather than limiting it to displaying security alerts.

---

# 🧠 Core Cybersecurity Concepts Demonstrated

Defentra demonstrates practical implementation of:

* Intrusion Detection Systems (IDS)
* Intrusion Prevention Systems (IPS)
* Web Application Firewalls
* OWASP-style application-layer threat detection
* SQL Injection detection
* XSS detection
* Rate limiting
* Brute-force protection
* Machine Learning classification
* SIEM architecture
* Security event correlation
* Threat intelligence
* IP geolocation
* Automated incident response
* Security alerting
* SOC dashboards
* API security

---

# 🧪 Testing Evidence

The platform has been tested using simulated security events.

For example, the SIEM successfully recorded multiple:

```text
WAF_SQLI_BLOCK
```

events with:

```text
Severity: Critical
Source: 127.0.0.1
```

along with timestamps and descriptions.

This demonstrates the complete flow from **WAF detection → active defense → SIEM logging**.

---

# 🔮 Future Improvements

Potential future development areas include:

### Advanced Risk Scoring

Combine multiple events from the same IP/user into a unified risk score.

```text
Low Network Threat
       +
Suspicious Email
       +
Repeated Login Attempts
       ↓
Aggregate Risk Score
       ↓
Critical
```

### Advanced Threat Intelligence

Integrate:

* IOC databases
* Malicious IP reputation
* Domain reputation
* Malware indicators

### Dashboard Improvements

Add:

* Global attack map
* Attack timeline
* Threat analytics
* Charts
* Security statistics
* Risk score visualization
* Attack source visualization

### Reporting

Add:

```text
CSV Reports
PDF Security Reports
Compliance Reports
```

### Production Deployment

Potential deployment improvements include:

* Docker
* PostgreSQL
* Production ASGI configuration
* Environment-based configuration
* Authentication
* HTTPS
* Secure secret management
* Multi-user SOC access

The project documentation also identifies dashboard enrichment, reporting, end-to-end testing, Docker, and production deployment as possible next steps.

---

# ⚠️ Security Disclaimer

Defentra is a cybersecurity research, development, and educational platform.

Only use the active defense and attack simulation capabilities on systems and networks that you own or have explicit permission to test.

The attack simulation tools are intended for controlled testing environments.

---

# 👨‍💻 Project Status

```text
████████████████████████████████  Core Platform
████████████████████████████████  WAF
████████████████████████████████  Active Defense
████████████████████████████████  ML Network Detection
████████████████████████████████  SIEM
████████████████████████████████  Threat Intelligence
████████████████████████████████  Webhook Alerts
████████████████████████████████  SOC Dashboard
```

**Current Status: Core platform implemented and integrated.**

---

# ⭐ Project Highlights

> **Defentra doesn't just detect threats — it creates a complete security response pipeline.**

```text
Detect
  ↓
Classify
  ↓
Assess Severity
  ↓
Block
  ↓
Store Evidence
  ↓
Enrich Intelligence
  ↓
Notify Security Team
  ↓
Visualize in SOC
```

---

## 📜 License

This project is intended for educational, research, and authorized cybersecurity testing purposes.

Choose an appropriate open-source license before publishing the repository publicly.

---

## 👨‍💻 Author

**Ansh Burnwal**

B.Tech Computer Science & Engineering

### Defentra

**AI-Powered Cybersecurity Threat Detection, SIEM & Active Defense Platform**
