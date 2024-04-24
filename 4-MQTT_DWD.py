import json
import requests
import paho.mqtt.client as mqtt

# Konfiguration der TTN-Anwendung
app_id = "XXXXXXXXXXXXXXXXX"
access_key = "XXXXXXXXXXXXXXXXXX"
mqtt_server = "eu1.cloud.thethings.network"
mqtt_port = 1883
topic = f"v3/{app_id}@ttn/devices/+/up"

# Callback-Funktion für die Verbindung
def on_connect(client, userdata, flags, rc):
    print(f"Mit Ergebniscode {rc} verbunden")
    client.subscribe(topic)

# Callback-Funktion für den Empfang von Nachrichten
def on_message(client, userdata, msg):
    print(f"Nachricht erhalten zum Thema: {msg.topic}")
    payload = msg.payload.decode('utf-8')
    data = json.loads(payload)

    # Extrahiere die Daten aus der MQTT-Nachricht
    mqtt_temperature = data['uplink_message']['decoded_payload'].get('t')
    mqtt_humidity = data['uplink_message']['decoded_payload'].get('h')
    mqtt_winddirection = data['uplink_message']['decoded_payload'].get('wd')
    mqtt_windspeed = data['uplink_message']['decoded_payload'].get('ws')
    mqtt_rainamount = data['uplink_message']['decoded_payload'].get('r')

    if all(data is not None for data in [mqtt_temperature, mqtt_humidity, mqtt_winddirection, mqtt_windspeed, mqtt_rainamount]):
        print(f"Wetterstation-Daten - Temperatur: {mqtt_temperature} °C, Luftfeuchtigkeit: {mqtt_humidity}%, Windrichtung: {mqtt_winddirection}°, Windgeschwindigkeit: {mqtt_windspeed/100} km/h, Regenmenge: {mqtt_rainamount} mm")

        # Abrufen der WeatherAPI-Daten
        API_key = "XXXXXXXXXXXXXXXXX"
        weatherapi_url = f"http://api.weatherapi.com/v1/current.json?key={API_key}&q=Dortmund"
        response = requests.get(weatherapi_url)
        weatherapi_data = response.json()

        # Extrahieren der WeatherAPI-Daten
        weatherapi_temperature = weatherapi_data['current']['temp_c']
        weatherapi_humidity = weatherapi_data['current']['humidity']
        weatherapi_wind_direction = weatherapi_data['current']['wind_degree']
        weatherapi_wind_speed = weatherapi_data['current']['wind_kph']
        weatherapi_rain_amount = weatherapi_data['current']['precip_mm']

        print(f"WeatherAPI-Daten - Temperatur in Dortmund: {weatherapi_temperature} °C, Luftfeuchtigkeit: {weatherapi_humidity}%, Windrichtung: {weatherapi_wind_direction}°, Windgeschwindigkeit: {weatherapi_wind_speed} km/h, Regenmenge: {weatherapi_rain_amount} mm")

        # Berechnen der Differenzen
        temp_difference = abs(float(mqtt_temperature) - weatherapi_temperature)
        humidity_difference = abs(float(mqtt_humidity) - weatherapi_humidity)
        wind_direction_difference = abs(float(mqtt_winddirection) - weatherapi_wind_direction)
        wind_speed_difference = abs(float(mqtt_windspeed) - weatherapi_wind_speed)
        rain_amount_difference = abs(float(mqtt_rainamount) - weatherapi_rain_amount)
        print(f"Differenz - Temperatur: {temp_difference} °C, Luftfeuchtigkeit: {humidity_difference}%, Windrichtung: {wind_direction_difference}°, Windgeschwindigkeit: {wind_speed_difference/100} km/h, Regenmenge: {rain_amount_difference} mm")
    else:
        print("Daten für Temperatur, Luftfeuchtigkeit, Windrichtung, Windgeschwindigkeit oder Regenmenge nicht in der MQTT-Nachricht gefunden.")


client = mqtt.Client()
client.username_pw_set(app_id, access_key)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server, mqtt_port, 60)
client.loop_forever()
