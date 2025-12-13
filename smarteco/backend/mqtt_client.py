import paho.mqtt.client as mqtt
import json
import os
from state import update_telemetry

MQTT_BROKER = "test.mosquitto.org" # Public broker for demo if local not available
MQTT_PORT = 1883
TOPIC = "smarteco/#"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        # Expected topic: smarteco/energy/blockA
        # Expected payload: {"value": 123, ...}
        parts = msg.topic.split("/")
        if len(parts) >= 2:
            resource = parts[1] # energy, water, waste
            payload = json.loads(msg.payload.decode())
            if "value" in payload:
                update_telemetry(resource, float(payload["value"]))
    except Exception as e:
        print(f"Error parsing MQTT: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start() # Runs in background thread
    except Exception as e:
        print(f"MQTT Connection failed ({e}). Using simulator only.")
