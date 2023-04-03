#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h >
#include <WiFiManager.h>
#include <Ticker.h>

const int intervalo = 5; // Intervalo en segundos entre cada publicación
unsigned long lastPublish = 0; // Momento en que se envió el último mensaje


// WiFiManager and PubSubClient objects
WiFiManager wifiManager;
WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Variables para el MQTT Broker
const char *mqtt_broker = "test.mosquitto.org"; // Enter your WiFi or Ethernet IP
const char *topic = "test/topic";
const int mqtt_port = 1883;
Ticker ticker;

void wifiConnect(){
  // Descomentar para resetear configuración
  //wifiManager.resetSettings();

  // Cremos AP y portal cautivo y comprobamos si
  // se establece la conexión
  if(!wifiManager.autoConnect("ESP8266Temp")){
    Serial.println("Fallo en la conexión (timeout)");
    ESP.reset();
    delay(1000);
  }

  Serial.println("Ya estás conectado");
}

void mqttServerConnect(){
  //Connecting to a mqtt broker  
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
 
  String client_id = "esp8266-client-";
  client_id += String(WiFi.macAddress());
  
  // Loop hasta que esté conectado
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    // Intenta conectarse
    if (client.connect(client_id.c_str())) {
      Serial.println("Conectado!");
      // Si nos conectamos correctamente, suscribimos y publicamos
      client.subscribe(topic);
      client.publish(topic, "Conexion restablecida!");
    } else {
      Serial.print("Falló con error: ");
      Serial.print(client.state());
      Serial.println("Intentamos de nuevo en 5 segundos");
      // Espera 5 segundos antes de reintentar
      delay(5000);
    }
  }  
}

void mqttServerPub(){
  // Establece el intervalo de tiempo para enviar mensajes al broker MQTT
  // Loop hasta que esté conectado
  ticker.attach(intervalo, [](){
    // Verifica si ha pasado suficiente tiempo desde la última publicación
    unsigned long now = millis();
    if (now - lastPublish >= intervalo * 1000) {
      // Publica un mensaje en el topic
      client.publish(topic, "Hello From ESP8266!");
      // Actualiza el momento en que se envió el último mensaje
      lastPublish = now;
    }
  });
}

void setup() {
  // Set software serial baud to 9600;
  Serial.begin(9600);
  wifiConnect();  
  mqttServerConnect();
  mqttServerPub();
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");

  for (int i = 0; i < length; i++) {
      Serial.print((char) payload[i]);
  }

  Serial.println();
  Serial.println(" - - - - - - - - - - - -");
}

void loop() {
  client.loop();
  // Da un breve tiempo de espera para permitir que otros procesos se ejecuten  
  yield();
}
