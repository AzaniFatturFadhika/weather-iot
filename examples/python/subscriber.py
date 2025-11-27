# Example: Python MQTT Subscriber

Simple Python script to subscribe to weather data.

## Installation

```bash
pip install paho-mqtt
```

## Usage

```python
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Broker Configuration
BROKER = "broker.emqx.io"
PORT = 1883
USERNAME = "emqx"
PASSWORD = "public"
TOPIC = "weather/station/data"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(TOPIC)
    print(f"Subscribed to topic: {TOPIC}")

def on_message(client, userdata, msg):
    try:
        # Parse JSON
        data = json.loads(msg.payload.decode())
        
        # Extract data
        station_id = data.get('stationID', 'Unknown')
        station_name = data.get('name', 'Unknown')
        timestamp = data.get('observationDate', datetime.now().isoformat())
        
        # Temperature
        temp = data.get('temperature', {})
        temp_value = temp.get('value', 'N/A')
        temp_unit = temp.get('unitText', '')
        
        # Humidity
        hum = data.get('humidity', {})
        hum_value = hum.get('value', 'N/A')
        hum_unit = hum.get('unitText', '')
        
        # Pressure
        press = data.get('atmosphericPressure', {})
        press_value = press.get('value', 'N/A')
        press_unit = press.get('unitText', '')
        
        # Display
        print("\n" + "="*50)
        print(f"📡 {station_name} ({station_id})")
        print(f"🕒 {timestamp}")
        print(f"🌡️  Temperature: {temp_value}{temp_unit}")
        print(f"💧 Humidity: {hum_value}{hum_unit}")
        print(f"🔽 Pressure: {press_value}{press_unit}")
        print("="*50)
        
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON")
    except Exception as e:
        print(f"❌ Error: {e}")

# Create MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect and loop
print("🔌 Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)
client.loop_forever()
```

## Run

```bash
python subscriber.py
```

## Output Example

```
🔌 Connecting to MQTT broker...
Connected to MQTT broker with code 0
Subscribed to topic: weather/station/data

==================================================
📡 Kec. Semarang Utara (TX001)
🕒 2025-11-23T12:00:00+07:00
🌡️  Temperature: 28.50°C
💧 Humidity: 65.20%
🔽 Pressure: 1013.25hPa
==================================================
```
