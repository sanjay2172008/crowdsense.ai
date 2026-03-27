#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Traffic Signal LEDs
#define LED_RED    25   // GPIO 25 - Red LED (High crowd - Don't go!)
#define LED_YELLOW 26   // GPIO 26 - Yellow LED (Medium crowd - Caution)
#define LED_GREEN  27   // GPIO 27 - Green LED (Low crowd - Safe!)
#define LED_STATUS 2    // Built-in LED (WiFi connected)

// ============== CONFIGURATION ==============
// CHANGE THESE TO YOUR WIFI CREDENTIALS
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// CHANGE THIS TO YOUR DEPLOYED APP URL
const char* serverUrl = "https://your-app.railway.app";

// Bus/Hospital/Temple to monitor
const char* queryParam = "q=12b";  // q=12b (bus), q=apollo (hospital), q=meenakshi (temple)
// ==========================================

// Update interval (milliseconds)
const long updateInterval = 10000;  // Update every 10 seconds
unsigned long previousUpdate = 0;

void setup() {
  Serial.begin(115200);
  
  // Initialize LED pins
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  
  // All LEDs off initially
  allLEDsOff();
  
  // Connect to WiFi
  connectWiFi();
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousUpdate >= updateInterval) {
    previousUpdate = currentMillis;
    fetchAndUpdateLEDs();
  }
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_STATUS, LOW);
    connectWiFi();
  } else {
    digitalWrite(LED_STATUS, HIGH);
  }
}

void connectWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    blinkStatusLED();
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi Connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_STATUS, HIGH);
  } else {
    Serial.println("");
    Serial.println("WiFi Failed! Check credentials.");
  }
}

void blinkStatusLED() {
  digitalWrite(LED_STATUS, HIGH);
  delay(100);
  digitalWrite(LED_STATUS, LOW);
}

void allLEDsOff() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
}

void fetchAndUpdateLEDs() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(serverUrl) + "/api/bus?" + queryParam;
  
  Serial.println("Fetching: " + url);
  
  http.begin(url);
  http.setTimeout(10000);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    Serial.println("Response: " + payload);
    
    // Parse JSON
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);
    
    if (!error) {
      const char* status = doc["status"] | "Unknown";
      int count = doc["count"] | 0;
      
      updateTrafficLEDs(status);
      Serial.print("Count: ");
      Serial.print(count);
      Serial.print(" - Status: ");
      Serial.println(status);
    } else {
      Serial.println("JSON Parse Error");
      blinkAllLEDsError();
    }
  } else {
    Serial.print("HTTP Error: ");
    Serial.println(httpCode);
    blinkAllLEDsError();
  }
  
  http.end();
}

void updateTrafficLEDs(const char* status) {
  allLEDsOff();
  
  if (strcmp(status, "High") == 0) {
    // Red LED ON - Crowded
    digitalWrite(LED_RED, HIGH);
    Serial.println(">>> RED LED ON - HIGH CROWD");
  } 
  else if (strcmp(status, "Medium") == 0) {
    // Yellow LED ON - Moderate
    digitalWrite(LED_YELLOW, HIGH);
    Serial.println(">>> YELLOW LED ON - MEDIUM CROWD");
  } 
  else if (strcmp(status, "Low") == 0) {
    // Green LED ON - Low
    digitalWrite(LED_GREEN, HIGH);
    Serial.println(">>> GREEN LED ON - LOW CROWD");
  }
  else {
    // All blink - Unknown status
    blinkAllLEDsError();
  }
}

void blinkAllLEDsError() {
  for (int i = 0; i < 3; i++) {
    allLEDsOff();
    delay(200);
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_YELLOW, HIGH);
    digitalWrite(LED_GREEN, HIGH);
    delay(200);
  }
  allLEDsOff();
}
