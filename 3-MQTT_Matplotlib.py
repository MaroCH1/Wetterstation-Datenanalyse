import json
import requests
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# MQTT Verbindungsparameter
app_id = "XXXXXXXXXXX"  
access_key = "XXXXXXXXXXXXXXX"
mqtt_server = "eu1.cloud.thethings.network"
mqtt_port = 1883
topic = f"v3/{app_id}@ttn/devices/+/up"

# Initialisieren der Listen zur Datenspeicherung und Zeitstempel
temperatures = []
humidities = []
wind_directions = []
wind_speeds = []
rain_amounts = []
timestamps = []

# Schwellenwert definieren
plot_threshold = 10
message_count = 0

# Callback, wenn eine connect-Antwort vom Server erhält
def on_connect(client, userdata, flags, rc):
    print(f"Verbunden mit Ergebniscode {rc}")
    client.subscribe(topic)

# Callback, wenn eine PUBLISH-Nachricht vom Server empfangen wird
def on_message(client, userdata, msg):
    global message_count
    payload = msg.payload.decode('utf-8')
    data = json.loads(payload)

    if 'decoded_payload' in data['uplink_message']:
        temp = data['uplink_message']['decoded_payload'].get('t')
        humid = data['uplink_message']['decoded_payload'].get('h')
        windD = data['uplink_message']['decoded_payload'].get('wd')
        windS = data['uplink_message']['decoded_payload'].get('ws')
        rainA = data['uplink_message']['decoded_payload'].get('r')
        
        received_at = data.get('received_at')

        if all(data is not None for data in [temp, humid, windD, windS, rainA, received_at]):
            temperatures.append(float(temp))
            humidities.append(float(humid))
            wind_directions.append(float(windD))
            wind_speeds.append(float(windS/100))
            rain_amounts.append(float(rainA))
            timestamps.append(datetime.fromisoformat(received_at.rstrip('Z')))

            
            print(f"Empfangene Daten - Te͏mper͏ature: {temp} °C, Humidity: {humid} %, Windrichtung: {windD} Grad, Windgeschwindigkeit: {windS/100} Km/h, Niederschlag: {rainA} mm")
            message_count += 1

            if message_count >= plot_threshold:
                plot_data()
                message_count = 0  

# Funktion zum Zeichnen der Daten
def plot_data():
    plt.figure(figsize=(14, 11))

    # Temperatur zeichnen
    plt.subplot(4, 1, 1)
    plt.plot(timestamps, temperatures, '-r')
    plt.title('Temperature, , Windrichtung, Windgeschwindigkeit und Niederschlag über Zeit')
    plt.ylabel('Temperatur (°C)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()

    # Luftfeuchtigkeit zeichnen
    plt.subplot(4, 1, 2)
    plt.plot(timestamps, humidities, '-b')
    plt.ylabel('Humidity (%)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()

    # Windrichtung zeichnen
    plt.subplot(4, 1, 3)
    plt.plot(timestamps, wind_directions, '-g')
    plt.ylabel('Windrichtung (Grad)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()

    # Windgeschwindigkeit zeichnen
    plt.subplot(4, 1, 4)
    plt.plot(timestamps, wind_speeds, '-c')
    plt.xlabel('Zeit')
    plt.ylabel('Windgeschwindigkeit (Km/h)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()
    # Niederschlag zeichnen
    plt.subplot(4, 1, 3)
    plt.plot(timestamps, rain_amounts, '-g')
    plt.ylabel('Niederschlag (mm)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()

#  Starten des MQTT-Clients
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(app_id, access_key)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_forever()
