# 🛡️ GCP Firewall Auto-Updater

A smart Python utility that detects your machine's current **Public IPv4 address** and automatically whitelists it in a specific **Google Cloud Platform (GCP)** Firewall Rule.

## ✨ Features

* **🔍 Auto-Detection**: Automatically fetches your public IP using a secure cloud function.
* **🌐 IPv4 Enforcement**: Includes a custom "Monkey Patch" to ensure network compatibility by forcing IPv4 resolution (similar to `curl -4`).
* **⚡ Smart Patching**: It doesn't overwrite your firewall! It fetches existing IPs, checks if you are already there, and appends your new IP if necessary.
* **☁️ Native GCP Integration**: Uses the official `google-cloud-compute` v1 library.

---

## 🛠️ How It Works: The "Monkey Patch"

This script uses a clever trick to handle DNS resolution. By overriding `socket.getaddrinfo`, we filter out IPv6 addresses before the `requests` library even sees them.

```python
# The "Gatekeeper" logic:
return [res for res in responses if res[0] == socket.AF_INET]

```

* **`res`**: The result we keep.
* **`for res in responses`**: Looking at every available IP address.
* **`if res[0] == socket.AF_INET`**: Only letting the guest in if they are IPv4!

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have the Google Cloud SDK authenticated on your machine:

```bash
gcloud auth application-default login

```

### 2. Installation

Install the required dependencies:

```bash
pip install requests google-cloud-compute

```

### 3. Configuration

Open `firewall-update-2.py` and update your project details:

```python
PROJECT_ID = "your-gcp-project-id"
FIREWALL_RULE_NAME = "your-firewall-rule-name"

```

### 4. Usage

Run the script whenever your IP changes or you move to a new network:

```bash
python3 firewall-update-2.py

```

---

## 📋 Script Logic Flow

1. **Hijack Sockets**: Force the system to prefer IPv4.
2. **Get IP**: Call the external API to find your public address.
3. **Fetch Firewall**: Connect to GCP and download the current `source_ranges` for your rule.
4. **Compare**: Check if your IP (`/32`) is already in the list.
5. **Update**: If missing, append the new IP and `patch` the firewall rule back to the cloud.

---

## ⚠️ Requirements

* **Python 3.6+**
* **GCP Permissions**: The service account or user running this script must have `compute.firewalls.get` and `compute.firewalls.update` permissions.

---
