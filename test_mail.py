import requests

EMAIL_API_URL = "http://localhost:8000/api/email-alert"

sample_phishing_email = {
    "sender": "security-update@bank-verification-login.com",
    "subject": "Action Required: Your account has been locked",
    "body_snippet": "Dear user, please click the secure link below immediately to restore your account access or it will be deleted.",
    "prediction": "Phishing",
    "confidence_score": 0.98,
    "contains_suspicious_url": True,
}

print("[*] Sending test phishing email alert to Defentra backend...")
response = requests.post(EMAIL_API_URL, json=sample_phishing_email)

if response.status_code == 200:
    print("[+] Success! Email alert registered in Defentra backend.")
    print(response.json())
else:
    print("[-] Failed to send email alert.")
