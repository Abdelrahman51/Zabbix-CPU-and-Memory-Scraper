# Zabbix Server Utilization Scraper

A Python tool that logs into a Zabbix web frontend, walks the host list, and pulls **CPU utilization, memory utilization, and per-disk space usage** for every server it finds — then exports everything into a single Excel report.

## The Problem It Solves

Zabbix's UI is great for real-time monitoring, but pulling a clean, shareable **utilization report across all hosts** usually means clicking through each server one by one, or writing custom API integrations. This script automates that: point it at your Zabbix frontend, and it produces a ready-to-share `servers_utilization.xlsx` with CPU, memory, and disk space for every host — useful for capacity planning, monthly health reports, or handing a snapshot to a client/manager without giving them Zabbix access.

## Features

- Authenticates to the Zabbix web frontend using a session (credentials pulled from environment variables, never hardcoded)
- Automatically discovers all hosts visible on the monitoring page
- Extracts CPU utilization, memory utilization, and disk space (used/total/utilization %) for each host, across all drive letters
- Outputs a single, clean Excel file — no manual copy-pasting

## How It Works

1. Logs into the Zabbix frontend with a POST request and keeps the session alive using `requests.Session()`.
2. Parses the host overview page with BeautifulSoup to collect each host's ID, name, and IP.
3. For each host, requests its detail page and parses out CPU, memory, and per-drive disk metrics.
4. Compiles everything into a `pandas` DataFrame and writes it to `servers_utilization.xlsx`.

## Requirements

- Python 3.8+
- A Zabbix frontend URL you have valid login access to
- Packages listed in [`requirements.txt`](./requirements.txt)

## Installation

```bash
git clone https://github.com/Abdelrahman51/Zabbix-CPU-and-Memory-Scraper.git
cd Zabbix-CPU-and-Memory-Scraper
pip install -r requirements.txt
```

## Setup

The script reads your Zabbix credentials from environment variables — **never edit credentials directly into the code**.

```bash
export LOGIN_NAME="your_zabbix_username"
export LOGIN_PASSWORD="your_zabbix_password"
```

On Windows (PowerShell):

```powershell
$env:LOGIN_NAME="your_zabbix_username"
$env:LOGIN_PASSWORD="your_zabbix_password"
```

You'll also need to edit three URLs near the top of `zabbix_server_data_extractor.py` to match your environment:

| Variable | What it should point to |
|---|---|
| `login_url` | Your Zabbix login endpoint, e.g. `https://zabbix.yourcompany.com/index.php` |
| `target_url` | The Zabbix host overview / monitoring page you want to scrape |
| `server_link` (template) | The per-host detail page URL, with the host ID appended |

## Usage

```bash
python zabbix_server_data_extractor.py
```

On success, you'll get a `servers_utilization.xlsx` file in the project folder containing one row per server with CPU %, memory %, and per-drive disk usage.

## Sample Output

| Server Name | IP | CPU Utilization | Memory Utilization | C::Space | C::Total Space | C::Used Space |
|---|---|---|---|---|---|---|
| WEB-SRV-01 | 10.0.0.11 | 34% | 61% | 42% | 100 GB | 42 GB |
| DB-SRV-02 | 10.0.0.12 | 78% | 85% | 67% | 500 GB | 335 GB |

*(sample data for illustration — your actual output will reflect your environment)*

## Notes & Limitations

- Built against the Zabbix web frontend (HTML scraping), not the official Zabbix API — this was intentional for environments where API access isn't available, but a future version could migrate to the [Zabbix API](https://www.zabbix.com/documentation/current/en/manual/api) for a more robust, version-stable integration.
- SSL verification is disabled (`verify=False`) for environments using self-signed certificates — if your Zabbix instance has a valid certificate, remove this for better security.

## Author

Built by **Abdelrahman Elsayed** — NOC Analyst / Network Engineer (CCNA, CompTIA Security+, SolarWinds SCP, ITIL v5 Foundation).
Specializing in network monitoring platforms (SolarWinds, PRTG, Zabbix) and Python/Ansible automation for IT operations.

[LinkedIn]([#](https://www.linkedin.com/in/abdelrahman-elsayed--/)) · [GitHub](https://github.com/Abdelrahman51)
