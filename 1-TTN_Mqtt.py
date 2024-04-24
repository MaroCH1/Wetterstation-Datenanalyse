import paho.mqtt.client as mqtt
import json

# Verbindungsparameter und Topic einstellen
app_id = "mkr1123"
access_key = "NNSXS.3WUVUW55QUW4GJHR47CW7LRZXGRY33ADAUVHNJA.WFHSLOJMN2OJEQ52YFT3EV6J7ZQZPPECFBF62SJN2VUXHLVVXY7A"
mqtt_server = "eu1.cloud.thethings.network"
mqtt_port = 1883
topic = f"v3/{app_id}@ttn/devices/+/up"

def on_connect(client, userdata, flags, rc):
    print("Verbunden mit Ergebniscode " + str(rc))
    # Abonniere das Topic, um Nachrichten zu empfangen
    client.subscribe(topic)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')  # Dekodiere den Byte-String


    data = json.loads(payload)


    if 'decoded_payload' in data['uplink_message']:
        temp = data['uplink_message']['decoded_payload'].get('t', 'N/A')
        humid = data['uplink_message']['decoded_payload'].get('h', 'N/A')
        windD = data['uplink_message']['decoded_payload'].get('wd', 'N/A')
        windS = data['uplink_message']['decoded_payload'].get('ws', 'N/A')
        rainamount = data['uplink_message']['decoded_payload'].get('r', 'N/A')

        print(f"Temperatur: {temp} °C")
        print(f"Luftfeuchtigkeit: {humid} %")
        print(f"Windrichtung: {windD} Grad")
        print(f"Windgeschwindigkeit: {windS/100} kmh")
        print(f"Niederschlag: {rainamount} mm")



# Initialisiere den Client und richte Callbacks ein
client = mqtt.Client()
client.username_pw_set(app_id, access_key)
client.on_connect = on_connect
client.on_message = on_message

# Verbinde und starte die Schleife
client.connect(mqtt_server, mqtt_port, 60)
client.loop_forever()
