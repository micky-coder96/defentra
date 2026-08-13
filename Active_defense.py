import subprocess
import platform


def block_malicious_ip(ip_address: str):
    os_name = platform.system()
    print(f"[*] INITIATING ACTIVE DEFENSE: Blocking malicious IP {ip_address}...")

    try:
        if os_name == "Windows":
            # Windows Firewall Command to add a block rule
            rule_name = f"Defentra_Block_{ip_address}"
            cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_address}'
            subprocess.run(cmd, shell=True, check=True)
            print(f"[+] Successfully blocked {ip_address} in Windows Firewall.")

        elif os_name == "Linux":
            # Linux IPTables command to drop traffic from IP
            cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
            subprocess.run(cmd, shell=True, check=True)
            print(f"[+] Successfully dropped packets from {ip_address} via iptables.")

    except Exception as e:
        print(f"[-] Failed to block IP {ip_address}: {e}")
