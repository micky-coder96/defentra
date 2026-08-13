import requests

# Replace with your actual Discord or Slack Webhook URL when ready
WEBHOOK_URL = "YOUR_DISCORD_OR_SLACK_WEBHOOK_URL_HERE"


def send_security_alert(
    event_type: str, source_ip: str, severity: str, description: str
):
    """Sends an asynchronous alert to a Discord/Slack channel for critical threats."""
    if WEBHOOK_URL == "YOUR_DISCORD_OR_SLACK_WEBHOOK_URL_HERE":
        # Skip if webhook isn't configured yet
        return

    payload = {
        "content": f"🚨 **DEFENTRA SECURITY ALERT** 🚨\n"
        f"• **Event:** {event_type}\n"
        f"• **Severity:** {severity}\n"
        f"• **Attacker IP:** {source_ip}\n"
        f"• **Details:** {description}"
    }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"[-] Failed to send webhook alert: {e}")
