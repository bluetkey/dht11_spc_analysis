#include <dht_nonblocking.h>
#define DHT_SENSOR_TYPE DHT_TYPE_11 //include the library

static const int DHT_SENSOR_PIN = 2;
DHT_nonblocking dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

int readingCount = 0;
const int maxReadings = 200; 

void setup() {
  Serial.begin(9600);
  Serial.println("index,temperature,humidity"); // CSV header
}

static bool measure_environment(float *temperature, float *humidity) {
  static unsigned long measurement_timestamp = millis();

  //take reading every 3s
  if (millis() - measurement_timestamp > 3000ul) {
    if (dht_sensor.measure(temperature, humidity) == true) {
      measurement_timestamp = millis();
      return true;
    }
  }
  return false;
}

void loop() {
  float temperature;
  float humidity;

  if (readingCount < maxReadings) {
    if (measure_environment(&temperature, &humidity) == true) {
      // Print clean CSV format: index,temp,humidity
      Serial.print(readingCount + 1);
      Serial.print(",");
      Serial.print(temperature, 1);
      Serial.print(",");
      Serial.println(humidity, 1);

      readingCount++;
    }
  } else {
    while (true) {} // stop forever after 200 readings
  }
}