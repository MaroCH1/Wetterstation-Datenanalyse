#include <ADSWeather.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <GP2YDustSensor.h>
#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>
#include <MKRWAN.h>
#include <ArduinoJson.h>
#include <Wire.h>

#define LED_PIN LED_BUILTIN
#define ANEMOMETER_PIN 4
#define VANE_PIN A2
#define RAIN_PIN 1
#define CALC_INTERVAL 1000
#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10
#define SEALEVELPRESSURE_HPA (1013.25)

const char *appEui = "XXXXXXXXXXXXXXX";                  //
const char *appKey = "XXXXXXXXXXXXXXXXXXXXX";  //


Adafruit_BME680 bme;  // I2C
unsigned long nextCalc;
unsigned long timer;
const uint8_t SHARP_LED_PIN = 7;
const uint8_t SHARP_VO_PIN = A1;
GP2YDustSensor dustSensor(GP2YDustSensorType::GP2Y1014AU0F, SHARP_LED_PIN, SHARP_VO_PIN);
ADSWeather ws1(RAIN_PIN, VANE_PIN, ANEMOMETER_PIN);
LoRaModem modem;

#define TESTLED 6

void setup_LED() {

  pinMode(LED_BUILTIN, OUTPUT); 
  digitalWrite(LED_BUILTIN, HIGH);   //LED ON

   }

void setup_lora() {
  Serial.begin(115200);
  //while (!Serial)
    ;

  if (!modem.begin(EU868)) {
    Serial.println("Failed to start module");
    while (1)
      ;
  }
  
  Serial.print("Your device EUI is: ");
  Serial.println(modem.deviceEUI());

  int connected = modem.joinOTAA(appEui, appKey);
  if (!connected) {
    Serial.println("Something went wrong; are you indoor? Move near a window and retry");
    while (1)
      ;
  }

  Serial.println("Successfully joined LoRaWAN network");

}

void setup_GP2Y_Dustsensor() {
  dustSensor.setBaseline(0.0);
  dustSensor.setCalibrationFactor(1);
  dustSensor.begin();
}

void setup_BME680() {
  delay(2000);
//while (!Serial)
    ;
  Serial.println(F("BME680 config"));

  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1)
      ;
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);
  Serial.println("BME config ready");
}

void setup() {
  pinMode(TESTLED, OUTPUT);

  Serial.begin(115200);
  delay(1000);
  

  attachInterrupt(digitalPinToInterrupt(RAIN_PIN), ws1.countRain, FALLING);
  attachInterrupt(digitalPinToInterrupt(ANEMOMETER_PIN), ws1.countAnemometer, FALLING);
  nextCalc = millis() + CALC_INTERVAL;



  setup_BME680();
  /*
         digitalWrite(TESTLED, HIGH);
  delay(500);
    digitalWrite(TESTLED, LOW);
   delay(500);
    digitalWrite(TESTLED, HIGH);
   delay(500);
    digitalWrite(TESTLED, LOW);
delay(500);
*/

  setup_GP2Y_Dustsensor();
  setup_lora();

setup_LED();

}

void loop() {
  timer = millis();

  int rainAmount;
  long windSpeed;
  long windDirection;
  int windGust;
  float temp;
  float humid;
  float altitude;
  float Dust_average;
  float Dust_Density;

  ws1.update();

  if (timer > nextCalc) {
    nextCalc = timer + CALC_INTERVAL;


    rainAmount = ws1.getRain();
    windSpeed = ws1.getWindSpeed();
    windDirection = ws1.getWindDirection();
    windGust = ws1.getWindGust();
    temp = bme.readTemperature() - 2.0;  // Adjust based on your sensor calibration
    humid = bme.readHumidity();
    altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
    Dust_average = dustSensor.getDustDensity();
    Dust_Density = dustSensor.getRunningAverage();


    String tempStr = String(temp, 2);
    String humidStr = String(humid, 2);

    // Create a JSON object
  DynamicJsonDocument doc(1024);
    doc["t"] = tempStr;
    doc["h"] = humidStr;
    doc["wd"] = windDirection;
    doc["r"] = rainAmount;
    doc["ws"] = windSpeed;





size_t jsonSize = measureJson(doc);
Serial.print("JSON Size: ");
Serial.println(jsonSize);


    // Serialize JSON to string
    String data;
    serializeJson(doc, data);
    // Print values to Serial Monitor
    Serial.print("Sending data: ");
    Serial.println(data);


    // Send the data over LoRaWAN
    modem.beginPacket();
    modem.print(data);
    modem.endPacket(true);  // 

    delay(60000);  // 
  }
}
