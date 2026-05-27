# OpenWrt DHCP Configuration Generator

This Python script automates the generation of static DHCP leases for OpenWrt routers. It fetches an HTML page containing network hardware tables, extracts the required data (MAC addresses, IPv4 addresses, and Hostnames), validates them, and generates a formatted `dhcp_hosts.conf` file.

## ✨ Features

* **Dynamic HTML Parsing:** Utilizes `BeautifulSoup` to locate and parse specific tables by their headings (e.g., "Static prototype IPs").
* **Strict Validation:**
  * **MAC Addresses:** Validates format via Regex and checks the multicast/broadcast bit.
  * **IPv4 Addresses:** Verifies that the IP belongs to the explicitly allowed subnet.
  * **Hostnames:** Ensures DNS-compliant naming conventions.
* **Cross-Table Collision Protection:** Uses global sets to prevent duplicate IP addresses or Hostnames across multiple tables, safely dropping invalid rows to protect network integrity.
* **CLI Logging Control:** Integrated `argparse` allows administrators to dynamically change the logging level via the command line.

## 🛠️ Requirements

The script requires **Python 3.10+** and the following external libraries:

```bash
pip install requests beautifulsoup4
```
*(Note: `re`, `ipaddress`, `logging`, and `argparse` are part of the Python Standard Library).*

## 🚀 Usage

You can run the script directly from the terminal. By default, it will only log `ERROR` level messages to the console.

```bash
python main.py
```

### Changing the Log Level
If you need to debug the parsing process or see more detailed warnings, you can override the default logging level using the `--loglevel` argument:

```bash
python main.py --loglevel DEBUG
python main.py --loglevel INFO
python main.py --loglevel WARNING
```

## ⚙️ How It Works

1. **Fetch:** The script downloads the HTML content from the target URL once.
2. **Parse:** It locates the table under the specified `<h2>` heading using a custom parsing function.
3. **Validate & Filter:** Iterates through the rows. If a MAC or IP is invalid, or if an IP/Hostname is already in use (duplicate), the entry is skipped/cleaned.
4. **Generate:** Outputs a valid OpenWrt configuration file named `dhcp_hosts.conf` in the root directory.

### Output Example (`dhcp_hosts.conf`)

```text
config host
    option name 'my-prototype-device'
    option ip '192.168.1.50'
    list mac '00:11:22:33:44:55'
    option dns '1'
```
