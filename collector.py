# collector/app.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "telemetry.db")

app = Flask(__name__)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB if not exists
def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        timestamp TEXT,
        temperature_c REAL,
        humidity_pct REAL,
        rpm INTEGER,
        accel_mps2 REAL
    )
    ''')
    conn.commit()
    conn.close()

@app.route("/telemetry", methods=["POST"])
def ingest():
    payload = request.get_json()
    # Basic validation
    required = ["device_id","timestamp","temperature_c","humidity_pct","rpm","accel_mps2"]
    if not payload or not all(k in payload for k in required):
        return jsonify({"error":"invalid payload"}), 400
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
      INSERT INTO telemetry (device_id,timestamp,temperature_c,humidity_pct,rpm,accel_mps2)
      VALUES (?,?,?,?,?,?)
    ''', (
        payload["device_id"],
        payload["timestamp"],
        payload["temperature_c"],
        payload["humidity_pct"],
        payload["rpm"],
        payload["accel_mps2"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"}), 200

@app.route("/telemetry/recent", methods=["GET"])
def recent():
    device = request.args.get("device_id")
    limit = int(request.args.get("limit", 100))
    conn = get_conn()
    c = conn.cursor()
    if device:
        rows = c.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT ?", (device,limit)).fetchall()
    else:
        rows = c.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
