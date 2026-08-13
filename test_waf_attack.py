import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🛡️ DEFENTRA WAF & ACTIVE DEFENSE SECURITY TEST")
print("=" * 60)

# --- Test 1: SQL Injection Attempt ---
sqli_payload = {"user_input": "admin' OR '1'='1' --"}
print("\n[1] Testing SQL Injection Defense...")
try:
    response = requests.post(f"{BASE_URL}/api/network-alert", json=sqli_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Server Response: {response.json()}")
except Exception as e:
    print(f"Request blocked/failed: {e}")

# --- Test 2: Cross-Site Scripting (XSS) Attempt ---
xss_payload = {"user_input": "<script>alert('HACKED!')</script>"}
print("\n[2] Testing Cross-Site Scripting (XSS) Defense...")
try:
    response = requests.post(f"{BASE_URL}/api/network-alert", json=xss_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Server Response: {response.json()}")
except Exception as e:
    print(f"Request blocked/failed: {e}")

# --- Test 3: Brute-Force Rate-Limiting Test ---
print("\n[3] Testing Rate-Limiting (Brute-Force) Defense...")
for i in range(1, 8):
    res = requests.post(f"{BASE_URL}/api/secure-login")
    print(f"Request #{i} -> Status: {res.status_code} | Response: {res.text}")
