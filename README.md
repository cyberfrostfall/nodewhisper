# nodewhisper

A lightweight sing-box proxy node delay monitor. It periodically tests latency for all outbound nodes and visualizes the results in a clean web dashboard.

## Features

- Automatic delay testing at configurable intervals
- Historical latency data with retention policy
- Web dashboard with real-time charts
- SQLite storage, zero external dependencies beyond Python

## Quick Start

```bash
pip install -r requirements.txt
cp config.ini.example config.ini
# Edit config.ini with your sing-box API details
python app.py
```

## Configuration

Copy `config.ini.example` to `config.ini` and fill in your sing-box API address and secret.

## Deployment

A systemd service file is included for running as a daemon:

```bash
sudo cp sing-box-monitor.service /etc/systemd/system/
sudo systemctl enable --now sing-box-monitor
```
