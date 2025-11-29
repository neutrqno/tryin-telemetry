# simulator/simulator.py
import time
import random
import requests
import uuid
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/telemetry"  
DEVICE_ID = str(uuid.uuid4())[:8]

def generate_reading():
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "temperature_c": round(20 + random.gauss(0,2) + 5*random.random(), 2),
        "humidity_pct": round(40 + random.gauss(0,5), 2),
        "rpm": int(1000 + random.gauss(0,100)),
        "accel_mps2": round(random.uniform(-2, 2), 3)
    }

def main():
    print("Simulator started, device:", DEVICE_ID)
    while True:
        data = generate_reading()
        try:
            r = requests.post(SERVER_URL, json=data, timeout=2)
            if r.status_code == 200:
                print("Sent:", data)
            else:
                print("Failed send:", r.status_code, r.text)
        except Exception as e:
            print("Error sending:", e)
        time.sleep(1) 
if __name__ == "__main__":
    main()
