import requests


def enrich_ip_address(ip_address: str):
    """Enriches an IP address with geolocation and basic threat intelligence data."""
    # Skip local loopback or private networks for external lookups
    if ip_address in ["127.0.0.1", "localhost", "0.0.0.0"] or ip_address.startswith(
        "192.168."
    ):
        return {
            "ip": ip_address,
            "country": "Local Network",
            "city": "Localhost",
            "isp": "Internal Loopback",
            "is_threat_proxy": False,
        }

    try:
        # Using a reliable public IP geolocation API endpoint
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "ip": ip_address,
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                }
    except Exception as e:
        print(f"[-] Geolocation lookup failed: {e}")

    return {"ip": ip_address, "country": "Unknown", "city": "Unknown", "isp": "Unknown"}
