import sqlite3
from datetime import datetime
import os

DB_PATH = "smarteco.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Telemetry table
    c.execute('''CREATE TABLE IF NOT EXISTS telemetry
                 (ts TEXT, resource TEXT, value REAL, location TEXT)''')
    # Alerts table
    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (ts TEXT, severity TEXT, resource TEXT, message TEXT, estimated_loss_inr REAL)''')
    conn.commit()
    conn.close()

def log_telemetry(resource, value, location="main"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO telemetry VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), resource, value, location))
    conn.commit()
    conn.close()

def log_alert(severity, resource, message, estimated_loss_inr):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO alerts VALUES (?, ?, ?, ?, ?)",
              (datetime.now().isoformat(), severity, resource, message, estimated_loss_inr))
    conn.commit()
    conn.close()
