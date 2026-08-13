import joblib
import requests
from scapy.all import sniff, IP, TCP, UDP

BACKEND_URL = "http://localhost:8000/api/network-alert"

print("[*] Loading Defentra ML Detection Engine...")
model = joblib.load("models/defentra_rf_model.pkl")
le = joblib.load("models/protocol_encoder.pkl")


def process_and_predict_packet(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        # Determine protocol
        proto_str = "tcp" if TCP in packet else ("udp" if UDP in packet else "other")
        pkt_len = len(packet)

        # Encode protocol safely using our saved encoder
        try:
            encoded_proto = le.transform([proto_str])[0]
        except ValueError:
            encoded_proto = 0  # Default fallback for unseen protocols

        # Features matching our training layout: [protocol_type, src_bytes, dst_bytes]
        features = [[encoded_proto, pkt_len, pkt_len]]

        # Predict using Machine Learning model
        prediction_array = model.predict(features)
        probabilities = model.predict_proba(features)

        prediction = prediction_array[0]
        confidence = float(max(probabilities[0]))

        # Protocol name for display
        proto_display = (
            "TCP" if TCP in packet else ("UDP" if UDP in packet else "OTHER")
        )

        payload = {
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "protocol": proto_display,
            "packet_size": pkt_len,
            "prediction": prediction,
            "confidence_score": confidence,
        }

        try:
            response = requests.post(BACKEND_URL, json=payload)
            if response.status_code == 200:
                print(
                    f"[ML DETECTION] {prediction} ({confidence*100:.1f}%) | {src_ip} ➔ {dst_ip}"
                )
        except requests.exceptions.ConnectionError:
            print("[-] Error: Could not connect to FastAPI backend.")


def start_defentra_ml_sniffer():
    print("[*] Defentra ML-Powered Sniffer is active... Listening for live traffic.")
    sniff(prn=process_and_predict_packet, store=False, count=20)


if __name__ == "__main__":
    start_defentra_ml_sniffer()
