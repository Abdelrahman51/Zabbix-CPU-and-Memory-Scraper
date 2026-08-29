"""
Zabbix Server Utilization Scraper
----------------------------------
Logs into a Zabbix web frontend, discovers all monitored hosts, and pulls
CPU utilization, memory utilization, and per-disk space usage for each host.
Results are exported to `servers_utilization.xlsx`.

Credentials are read from environment variables (LOGIN_NAME, LOGIN_PASSWORD)
and must never be hardcoded in this file.

Author: Abdelrahman Elsayed - NOC Analyst / Network Engineer
"""

import os
import warnings

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Zabbix's frontend may use a self-signed certificate in many internal
# environments, which raises noisy InsecureRequestWarning messages. We
# suppress them here since verify=False is used intentionally below.
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# --- Configuration -----------------------------------------------------
# Update these to match your Zabbix environment before running the script.
LOGIN_URL = "https://your_login_url.com"
TARGET_URL = "https://your_target_url.com"  # Host overview / monitoring page

# Drive letters to check for disk utilization on each host.
DISK_LABELS = [chr(c) for c in range(ord("C"), ord("Z") + 1)]


def login(session: requests.Session) -> requests.Response:
    """Authenticate to the Zabbix frontend and return the login response.

    Credentials are pulled from the LOGIN_NAME / LOGIN_PASSWORD environment
    variables so nothing sensitive ever lives in source control.
    """
    login_data = {
        "name": os.getenv("LOGIN_NAME"),
        "password": os.getenv("LOGIN_PASSWORD"),
        "autologin": "1",
        "enter": "Sign in",
    }
    return session.post(LOGIN_URL, data=login_data, verify=False)


def get_host_links(overview_html: str):
    """Parse the host overview page and return every host anchor tag
    that carries Zabbix's `data-menu-popup` host metadata."""
    soup = BeautifulSoup(overview_html, "html.parser")
    return [
        link
        for link in soup.find_all("a")
        if link.get("data-menu-popup") and "hostid" in link.get("data-menu-popup")
    ]


def extract_host_id(link) -> str:
    """Pull the numeric Zabbix host ID out of a link's data-menu-popup attribute."""
    data_menu_popup = link.get("data-menu-popup")
    start = data_menu_popup.find('"hostid":') + 9
    end = data_menu_popup.find("}", start)
    return data_menu_popup[start:end].strip(' "')


def extract_metric(soup: BeautifulSoup, label_text: str):
    """Find a labeled metric (e.g. 'CPU utilization') on a host detail page
    and return the value in the adjacent table cell, or None if not present."""
    label = soup.find("span", text=label_text)
    if not label:
        return None
    value_cell = label.find_parent("div").find_next("td").find_next_sibling("td")
    return value_cell.get_text(strip=True) if value_cell else None


def extract_disk_metrics(soup: BeautifulSoup) -> dict:
    """Extract space utilization, total space, and used space for every
    drive letter (C through Z) present on a host detail page."""
    disk_values = {}
    for label in DISK_LABELS:
        disk_values[f"{label}::Space "] = extract_metric(soup, f"{label}:: Space utilization")
        disk_values[f"{label}::Total Space "] = extract_metric(soup, f"{label}:: Total space")
        disk_values[f"{label}::Used Space"] = extract_metric(soup, f"{label}:: Used space")
    return disk_values


def get_server_info(session: requests.Session, link) -> dict:
    """Fetch and parse the full utilization detail (CPU, memory, disk) for
    a single host, given its overview page link element."""
    host_id = extract_host_id(link)
    server_name = link.get_text().strip()

    interface_element = link.find_next("td", class_="nowrap")
    interface_number = interface_element.get_text() if interface_element else "N/A"
    interface_number = interface_number.split(":")[0]

    server_link = f"{TARGET_URL}&filter_hostids%5B0%5D={host_id}"
    server_response = session.get(server_link, verify=False)

    if server_response.status_code != 200:
        print(f"Can't get access to details for host: {server_name}")
        return None

    server_soup = BeautifulSoup(server_response.text, "html.parser")

    return {
        "Server Name": server_name,
        "IP": interface_number,
        "CPU Utilization": extract_metric(server_soup, "CPU utilization"),
        "Memory Utilization": extract_metric(server_soup, "Memory utilization"),
        **extract_disk_metrics(server_soup),
    }


def main():
    session = requests.Session()
    login_response = login(session)

    if login_response.status_code != 200 or "You are not logged in" in login_response.text:
        print(f"Error: Login failed (Status code: {login_response.status_code})")
        return

    print("Successfully logged in!")

    target_response = session.get(TARGET_URL, verify=False)
    if target_response.status_code != 200:
        print(f"Error: Unable to retrieve the target page (Status code: {target_response.status_code})")
        return

    host_links = get_host_links(target_response.text)

    server_info = []
    for link in host_links:
        info = get_server_info(session, link)
        if info:
            server_info.append(info)

    df = pd.DataFrame(server_info)
    df.to_excel("servers_utilization.xlsx", index=False)
    print("Server information with Host ID has been saved to 'servers_utilization.xlsx' successfully!")


if __name__ == "__main__":
    main()
