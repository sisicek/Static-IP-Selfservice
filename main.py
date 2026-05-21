import requests
import re
import ipaddress
import logging
from bs4 import BeautifulSoup

def validate_mac(currentMac: str, macPattern: str) -> bool:
    if not re.match(macPattern, currentMac):
        logging.error(f"Wrong format of MAC address: {currentMac}")
        return False

    # checking the first two chars of the mac address
    macPrefixText = currentMac[:2]
    macPrefixDec = int(macPrefixText, 16)
    if macPrefixDec % 2 != 0:
        logging.error(f"MAC address is multicast/broadcast: {currentMac}")
        return False
    return True

def validate_ip(currentIpv4: str, allowedNetwork) -> bool:
    try:
        ip_object = ipaddress.ip_address(currentIpv4)
        if ip_object not in allowedNetwork:
            logging.error(f"IP adresa {currentIpv4} doesn't belong into our network")
            return False
        return True
    # catch in C#
    except ValueError:
        logging.error(f"Wrong format of IP address: {currentIpv4}")
        return False

def validate_hostname(cells_text: list, hostnameIndex: int, tableLength: int, dnsPattern: str) -> str | bool:
    currentHostname: str | bool = False
    
    if tableLength != len(cells_text) or cells_text[hostnameIndex] == "":
        currentHostname = False
    elif "." in cells_text[hostnameIndex]:
        cells_text[hostnameIndex] = cells_text[hostnameIndex].replace(".", "-")
        currentHostname = cells_text[hostnameIndex]
    else:
        currentHostname = cells_text[hostnameIndex]
        
    if currentHostname:
        if not re.match(dnsPattern, currentHostname):
            currentHostname = False
            
    return currentHostname

def generate_file(table: dict[str, dict]):
    with open("dhcp_hosts.conf", "w", encoding="utf-8") as f:
        for mac in sorted(table.keys()):
            row_data = table[mac]
            hostname = row_data["hostname"]
            ipv4 = row_data["ipv4"]

            f.write("config host\n")
            if hostname:
                f.write(f"    option name '{hostname}'\n")
            f.write(f"    option ip '{ipv4}'\n")
            f.write(f"    list mac '{mac}'\n")
            if hostname:
                f.write(f"    option dns '1'\n")

def main():
    url = "https://spsrakovnik.tech/hauner.vo.2023/PV"
    # url = "https://metalab.at/wiki/Netzwerk/Adressen"

    allowedNetwork = ipaddress.ip_network("192.168.0.0/16")

    hostnameIndex: int = 0
    macIndex: int = 0
    ipv4Index: int = 0
    ipv6Index: int = 0

    tableLength: int = 0 # number of columns in the table
    table: dict[str, dict] = {}

    dnsPattern: str = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
    macPattern: str = r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$"

    response = requests.get(url)

    # if we got HTML
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        target_heading = soup.find("h2", string="Static prototype IPs")
        if target_heading:
            target_table = target_heading.find_next("table")
            if target_table:
                print("Tabulka nalezena!\n")
                j: int = 0
                for row in target_table.find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    cells_text = [cell.get_text(strip=True).lower() for cell in cells]

                    # getting indexes of each columns to know where is hostname, mac address, etc.
                    if j == 0:
                        tableLength = len(cells_text)
                        i = 0
                        for cell in cells_text:
                            if "hostname" in cell:
                                hostnameIndex = i
                            elif "mac" in cell:
                                macIndex = i
                            elif "ipv4" in cell:
                                ipv4Index = i
                            elif "ipv6" in cell:
                                ipv6Index = i
                            i += 1
                        j += 1
                        # skipping the heading of the table
                        continue
                    
                    # saving data on the current row
                    currentMac: str = cells_text[macIndex]
                    currentIpv4: str = cells_text[ipv4Index]
                    currentIpv6: str = cells_text[ipv6Index]

                    # validating the mac address
                    if not validate_mac(currentMac, macPattern):
                        continue

                    # validating the ip address
                    if not validate_ip(currentIpv4, allowedNetwork):
                        continue
        
                    # validation the hostname
                    currentHostname = validate_hostname(cells_text, hostnameIndex, tableLength, dnsPattern)

                    # saving data into the dict
                    table[currentMac] = {
                        "ipv4": currentIpv4,
                        "ipv6": currentIpv6,
                        "hostname": currentHostname,
                    }

                generate_file(table)
    else:
        print(f"Chyba při stahování stránky. Status kód: {response.status_code}")

if __name__ == "__main__":
    main()
