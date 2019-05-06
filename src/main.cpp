#include <Arduino.h>
#include <WiFi.h>
#include "PubSubClient.h"

#define WIFI_SSID "bayuabi2"
#define WIFI_PASSWORD "87654321"

#define MQTT_HOST "192.168.43.151"
#define MQTT_PORT 1883

WiFiClient espClient;
PubSubClient client(espClient);

char c_debit[50];
char c_volume[50];
bool sendState = false;

#define WATERFLOW_PIN 22

volatile uint8_t tick = 0;

void ISR_FUNC();

unsigned long int currentTime = 0;
unsigned long int previousTime = 0;
unsigned long int previousTime2 = 0;
float volume, volumeTemp = 0;
int debit = 0;

String meteranID = "ABC123";

void setup() {
  Serial.begin(115200);

  attachInterrupt(WATERFLOW_PIN, ISR_FUNC, FALLING);

  Serial.print("Connecting to: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi Connected");
  Serial.print("Local IP: ");
  Serial.println(WiFi.localIP());

  client.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if(!client.connected()){
    while(!client.connected()){
    if(client.connect("")){
      Serial.println("Connected to MQTT Server");
    }
    else{
      Serial.println("Tidak Connect");
    }
  }
  }

  currentTime = millis();
  if (currentTime - previousTime >= 1000){
    previousTime = currentTime;

    debit = tick/8;

    volume = float(debit) / 60;
    volume = volumeTemp + volume;
    
    Serial.print("Debit: ");
    Serial.print(debit);
    Serial.print("   Volume: ");
    Serial.println(volume);

    tick = 0;
  }
  volumeTemp = volume;

  if(currentTime - previousTime2 >= 2000){
    previousTime2 = currentTime;

    if(!sendState){
      snprintf(c_debit, 50, "%d", debit);
      client.publish("debit", c_debit);
      sendState = !sendState;
    }
    else{
      snprintf(c_volume, 50, "%f", volume);
      client.publish("volume", c_volume);
      sendState = !sendState;
    }
  }
}

void ISR_FUNC(){
  tick++;
}


