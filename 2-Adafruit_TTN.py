import base64
import json
import paho.mqtt.client as mqtt

# Aktivieren des MQTT-Loggers
mqtt.Client().enable_logger(logger=None)

# TTN-Konfiguration
ttn_broker = 'eu1.cloud.thethings.network'
ttn_port = 1883
ttn_app_id = 'mkr1123'
ttn_access_key = 'NNSXS.3WUVUW55QUW4GJHR47CW7LRZXGRY33ADAUVHNJA.WFHSLOJMN2OJEQ52YFT3EV6J7ZQZPPECFBF62SJN2VUXHLVVXY7A'
ttn_topic = f'v3/{ttn_app_id}@ttn/devices/+/up'

# Adafruit Konfiguration
adafruit_username = 'hakatak'
adafruit_key = 'aio_VejT08Ed3HA6zVlhrWJuLa124oIN'
adafruit_broker = 'io.adafruit.com'
adafruit_port = 1883
temperature_feed = f'{adafruit_username}/feeds/tempfeed'
humidity_feed = f'{adafruit_username}/feeds/humfeed'
winddirection_feed = f'{adafruit_username}/feeds/winddirection'
rain_feed = f'{adafruit_username}/feeds/rainamount'
windspeed_feed = f'{adafruit_username}/feeds/windspeed'

# Initialisieren des MQTT-Clients für TTN
ttn_client = mqtt.Client()

# Initialisieren des MQTT-Clients für Adafruit IO
adafruit_client = mqtt.Client()
adafruit_client.username_pw_set(adafruit_username, adafruit_key)


def on_connect_ttn(client, userdata, flags, rc):
    if rc == 0:
        print("Mit TTN verbunden, Result Code " + str(rc))
        client.subscribe(ttn_topic)
    else:
        print(f"Fehler beim Verbinden mit TTN, Result Code {rc}")

# Callback-Funktion für den Empfang von Nachrichten von TTN
def on_message_ttn(client, userdata, msg):
    try:
        # Dekodierung der empfangenen Nachricht
        payload_raw = json.loads(msg.payload.decode())['uplink_message']['frm_payload']
        payload_decoded = base64.b64decode(payload_raw).decode()
        print(f"Nachricht von TTN empfangen: {payload_decoded}")

        # Extrahieren der Daten
        data = json.loads(payload_decoded)
        temp_value = data["t"]
        humidity_value = data["h"]
        winddirection_value = data["wd"]
        rain_value = data["r"]
        windspeed_value = data["ws"]

        # Veröffentlichen der Daten an Adafruit 
        adafruit_client.publish(temperature_feed, str(temp_value))
        adafruit_client.publish(humidity_feed, str(humidity_value))
        adafruit_client.publish(winddirection_feed, str(winddirection_value))
        adafruit_client.publish(rain_feed, str(rain_value))
        adafruit_client.publish(windspeed_feed, str(windspeed_value))

        print(f"Veröffentlicht auf Adafruit : Temperatur {temp_value}, Luftfeuchtigkeit: {humidity_value}, Niederschlag: {rain_value}, Windrichtung: {winddirection_value}, Windgeschwindigkeit: {windspeed_value/100}")
    except Exception as e:
        print(f"Fehler bei der Verarbeitung : {e}")

ttn_client.on_connect = on_connect_ttn
ttn_client.on_message = on_message_ttn
ttn_client.username_pw_set(ttn_app_id, password=ttn_access_key)

# Verbindung zu den MQTT-Brokern aufbauen
try:
    ttn_client.connect(ttn_broker, ttn_port, 60)
    adafruit_client.connect(adafruit_broker, adafruit_port, 60)
except Exception as e:
    print(f"Fehler beim Verbinden mit dem MQTT-Broker: {e}")


ttn_client.loop_start()
adafruit_client.loop_start()


