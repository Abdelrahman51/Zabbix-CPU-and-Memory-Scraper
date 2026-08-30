# Zabbix Server Utilization Scraper

A Python script that logs into a Zabbix web frontend, discovers all monitored hosts, and pulls CPU utilization, memory utilization, and per-disk space usage for each host — then exports everything to a single Excel report.

## Why this exists

Zabbix's web UI doesn't offer a simple one-click export that combines CPU, memory, and per-disk usage across all hosts into a single spreadsheet. Pulling this manually, host by host, is slow — especially in environments with dozens of monitored servers. This script automates that collection end-to-end.

## Features

- Authenticates to the Zabbix frontend using environment-variable credentials (never hardcoded)
- Automatically discovers every monitored host from the overview page
- Extracts CPU utilization, memory utilization, and per-drive (C–Z) space usage for each host
- Exports all results to a clean `servers_utilization.xlsx` report using pandas

## Requirements

- Python 3.8+
- Access to a Zabbix web frontend with valid login credentials

## Setup

```bash
pip install -r Requirements.txt
```

Set your Zabbix credentials as environment variables:

```bash
export LOGIN_NAME="your_zabbix_username"
export LOGIN_PASSWORD="your_zabbix_password"
```

Open `zabbix_server_data_extractor.py` and update the `LOGIN_URL` and `TARGET_URL` constants near the top of the file to match your Zabbix environment's login page and host overview page.

## Usage

```bash
python zabbix_server_data_extractor.py
```

The script will log in, discover all monitored hosts, and generate `servers_utilization.xlsx` in the current directory containing CPU, memory, and disk utilization for every host found.

## Example Output

The generated Excel file includes one row per host with columns for Server Name, IP, CPU Utilization, Memory Utilization, and per-drive space/total/used values.

## Notes

Built to speed up recurring NOC reporting tasks where a quick, consolidated utilization snapshot across all monitored servers is needed without manually opening each host's page in the Zabbix UI.
