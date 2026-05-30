import sqlite3
import configparser
import os
import requests
from flask import Flask, render_template, jsonify, request as flask_request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))

SINGBOX_API = config.get("singbox", "api_url")
SINGBOX_SECRET = config.get("singbox", "secret")
TEST_URL = config.get("singbox", "test_url")
DELAY_TIMEOUT = config.getint("singbox", "timeout")
CHECK_INTERVAL_MINUTES = config.getint("monitor", "interval")
RETENTION_HOURS = config.getint("monitor", "retention_hours")
PORT = config.getint("monitor", "port")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")

HEADERS = {"Authorization": f"Bearer {SINGBOX_SECRET}"}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS delay_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_name TEXT NOT NULL,
            delay_ms INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON delay_records(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_node_timestamp ON delay_records(node_name, timestamp)")
    conn.commit()
    conn.close()


def cleanup_old_data():
    conn = sqlite3.connect(DB_PATH)
    cutoff = (datetime.now() - timedelta(hours=RETENTION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("DELETE FROM delay_records WHERE timestamp < ?", (cutoff,))
    conn.commit()
    conn.close()


def get_all_proxies():
    try:
        resp = requests.get(f"{SINGBOX_API}/proxies", headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        proxies = data.get("proxies", )
        nodes = []
        skip_types = {"Selector", "URLTest", "Direct", "Reject", "Block", "DNS", "Fallback"}
        for name, info in proxies.items():
            if info.get("type") not in skip_types and not name.startswith("GLOBAL"):
                nodes.append(name)
        return nodes
    except Exception as e:
        print(f"[ERROR] Failed to get proxies: {e}")
        return []


def test_node_delay(node_name):
    try:
        resp = requests.get(
            f"{SINGBOX_API}/proxies/{requests.utils.quote(node_name)}/delay",
            params={"timeout": DELAY_TIMEOUT, "url": TEST_URL},
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("delay", None)
        return None
    except Exception:
        return None


def check_all_delays():
    nodes = get_all_proxies()
    if not nodes:
        return
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for node in nodes:
        delay = test_node_delay(node)
        conn.execute(
            "INSERT INTO delay_records (node_name, delay_ms, timestamp) VALUES (?, ?, ?)",
            (node, delay, now)
        )
    conn.commit()
    conn.close()
    cleanup_old_data()
    print(f"[{now}] Checked {len(nodes)} nodes")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/report")
def report():
    return render_template("index.html")


@app.route("/api/nodes")
def api_nodes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.now() - timedelta(hours=RETENTION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT DISTINCT node_name FROM delay_records WHERE timestamp >= ?", (cutoff,)
    ).fetchall()
    conn.close()
    return jsonify([row["node_name"] for row in rows])


@app.route("/api/delays")
def api_delays():
    hours = int(flask_request.args.get("hours", RETENTION_HOURS))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT node_name, delay_ms, timestamp FROM delay_records WHERE timestamp >= ? ORDER BY timestamp",
        (cutoff,)
    ).fetchall()
    conn.close()

    result = {}
    for row in rows:
        name = row["node_name"]
        if name not in result:
            result[name] = []
        result[name].append({"delay": row["delay_ms"], "time": row["timestamp"]})
    return jsonify(result)



@app.route("/api/report")
def api_report():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    now = datetime.now()
    cutoff = (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

    rows = conn.execute(
        "SELECT node_name, delay_ms, timestamp FROM delay_records WHERE timestamp >= ? ORDER BY node_name, timestamp",
        (cutoff,)
    ).fetchall()
    conn.close()

    node_data = {}
    for row in rows:
        name = row["node_name"]
        if name not in node_data:
            node_data[name] = []
        node_data[name].append({"delay": row["delay_ms"], "time": row["timestamp"]})

    nodes_stats = []
    for name, records in node_data.items():
        delays = [r["delay"] for r in records if r["delay"] is not None]
        total = len(records)
        timeout_count = total - len(delays)
        avg_delay = round(sum(delays) / len(delays)) if delays else None
        min_delay = min(delays) if delays else None
        max_delay = max(delays) if delays else None
        timeout_rate = round(timeout_count / total * 100, 1) if total > 0 else 0

        if avg_delay is None or timeout_rate > 20:
            status = "bad"
        elif avg_delay > 300:
            status = "bad"
        elif avg_delay > 100:
            status = "warning"
        else:
            status = "good"

        nodes_stats.append({
            "name": name,
            "avg_delay": avg_delay,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "timeout_count": timeout_count,
            "total_count": total,
            "timeout_rate": timeout_rate,
            "status": status
        })

    nodes_stats.sort(key=lambda x: (x["avg_delay"] is None, x["avg_delay"] or 9999))
    for i, node in enumerate(nodes_stats):
        node["rank"] = i + 1

    anomalies = []
    for name, records in node_data.items():
        delays = [r["delay"] for r in records if r["delay"] is not None]
        avg = sum(delays) / len(delays) if delays else 0

        consecutive_timeouts = 0
        timeout_start = None
        for r in records:
            if r["delay"] is None:
                if consecutive_timeouts == 0:
                    timeout_start = r["time"]
                consecutive_timeouts += 1
            else:
                if consecutive_timeouts >= 2:
                    anomalies.append({
                        "node": name,
                        "type": "consecutive_timeout",
                        "start": timeout_start,
                        "end": records[records.index(r) - 1]["time"],
                        "count": consecutive_timeouts
                    })
                consecutive_timeouts = 0
        if consecutive_timeouts >= 2:
            anomalies.append({
                "node": name,
                "type": "consecutive_timeout",
                "start": timeout_start,
                "end": records[-1]["time"],
                "count": consecutive_timeouts
            })

        if avg > 0:
            for r in records:
                if r["delay"] is not None and r["delay"] > avg * 3:
                    anomalies.append({
                        "node": name,
                        "type": "spike",
                        "time": r["time"],
                        "delay": r["delay"],
                        "avg": round(avg)
                    })

    anomalies.sort(key=lambda x: x.get("time") or x.get("start"), reverse=True)

    return jsonify({
        "period": {
            "start": cutoff,
            "end": now.strftime("%Y-%m-%d %H:%M:%S")
        },
        "nodes": nodes_stats,
        "anomalies": anomalies
    })


if __name__ == "__main__":
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_all_delays, "interval", minutes=CHECK_INTERVAL_MINUTES, next_run_time=datetime.now())
    scheduler.start()
    app.run(host="0.0.0.0", port=PORT)
