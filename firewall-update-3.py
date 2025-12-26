import requests
import socket
from google.cloud import compute_v1

# --- CONFIGURATION ---
PROJECT_ID = "our-project-1234"         # Replace with your GCP Project ID
FIREWALL_RULE_NAME = "firewallrule-12"  # Replace with your Firewall Rule name
# ---------------------

# This "forces" the socket to only look for IPv4 (AF_INET)
# It acts exactly like the -4 flag in curl
old_getaddrinfo = socket.getaddrinfo


def res_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]


socket.getaddrinfo = res_getaddrinfo


# ---------------------

def get_public_ip():
    """Fetches the public IP of the current machine."""
    url = 'https://get-ip-2-951077742824.us-central1.run.app'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        ip = response.json()['ip']
        print(f"✅ Detected Public IP: {ip}")
        return ip
    except Exception as e:
        print(f"❌ Failed to get public IP: {e}")
        return None


def add_ip_to_firewall(project_id, rule_name, new_ip):
    """Adds an IP to an existing GCP Firewall rule."""

    # 1. Initialize the Firewall Client
    client = compute_v1.FirewallsClient()

    # 2. Get the existing rule
    # We need the current list of IPs so we don't overwrite them
    try:
        firewall_rule = client.get(project=project_id, firewall=rule_name)
    except Exception as e:
        print(f"❌ Could not find firewall rule '{rule_name}': {e}")
        return

    # 3. Check and Append
    # We format the IP with /32 to denote a single IP address
    cidr_ip = f"{new_ip}/32"

    # Create a mutable list from the existing source_ranges
    current_ranges = list(firewall_rule.source_ranges)

    if cidr_ip in current_ranges:
        print(f"ℹ️  IP {cidr_ip} is already in the firewall rule. No changes needed.")
        return

    print(f"My current ranges: {current_ranges}")
    print(f"Adding {cidr_ip}...")

    current_ranges.append(cidr_ip)

    # 4. Prepare the Patch
    # We create a simplified Firewall object containing only the fields we want to change
    firewall_update = compute_v1.Firewall()
    firewall_update.source_ranges = current_ranges

    # 5. Send the Update (Patch)
    operation = client.patch(
        project=project_id,
        firewall=rule_name,
        firewall_resource=firewall_update
    )

    print("⏳ Updating firewall rule... (this may take a few seconds)")

    # Wait for the operation to complete
    operation.result()

    print(f"✅ Success! Added {cidr_ip} to {rule_name}.")


if __name__ == "__main__":
    my_ip = get_public_ip()
    if my_ip:
        add_ip_to_firewall(PROJECT_ID, FIREWALL_RULE_NAME, my_ip)
    else:
        print("file cannot be called")

