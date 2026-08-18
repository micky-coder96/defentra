import platform
import subprocess


def block_malicious_ip(ip_address: str):
    """
    Blocks a malicious IP using OS-level firewalls (Windows Netsh or Linux IPTables).
    Automatically skips loopback addresses to prevent local testing crashes.
    """
    # 1. Skip local loopback or test IPs to prevent breaking local testing
    if ip_address in ["127.0.0.1", "localhost", "::1", "10.0.2.15"]:
        print(
            f"[ACTIVE DEFENSE SIMULATION] Bypassing OS firewall block for local/test IP: {ip_address}"
        )
        return

    os_name = platform.system()
    print(
        f"[*] INITIATING ACTIVE DEFENSE: Blocking malicious IP {ip_address} on {os_name}..."
    )

    try:
        if os_name == "Windows":
            # Windows Firewall Command to add a block rule
            rule_name = f"Defentra_Block_{ip_address}"
            cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_address}'

            # Run command (Note: Windows requires PowerShell/CMD to be run as Administrator)
            subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            print(f"[+] Successfully blocked {ip_address} in Windows Firewall.")

        elif os_name == "Linux":
            # Linux IPTables command to drop traffic from IP
            cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
            subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            print(f"[+] Successfully dropped packets from {ip_address} via iptables.")

    except subprocess.CalledProcessError as e:
        print(
            f"[-] Failed to block IP {ip_address} at OS level. (Tip: Ensure your terminal has Administrator/Root privileges): {e.stderr.strip()}"
        )
    except Exception as e:
        print(f"[-] Unexpected error during active defense execution: {e}")
