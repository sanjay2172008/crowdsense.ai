#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============== CONFIGURATION ==============
// CHANGE THESE TO YOUR WIFI CREDENTIALS
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// CHANGE THIS TO YOUR DEPLOYED APP URL
const char* serverUrl = "https://your-app.railway.app";

// Bus/Hospital/Temple to monitor
const char* queryParam = "q=12b";  // Change this to search bus (e.g., q=apollo for hospital, q=meenakshi for temple)

// ==========================================

// OLED Configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Update interval (milliseconds)
const long updateInterval = 10000;  // Update every 10 seconds
unsigned long previousUpdate = 0;

// WiFi status LED
#define LED_WIFI 2  // Built-in LED on ESP32

void setup() {
  Serial.begin(115200);
  
  // Initialize LED
  pinMode(LED_WIFI, OUTPUT);
  digitalWrite(LED_WIFI, LOW);  // LED off initially
  
  // Initialize OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED allocation failed");
    while(1);
  }
  
  // Show startup screen
  displayStartup();
  
  // Connect to WiFi
  connectWiFi();
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousUpdate >= updateInterval) {
    previousUpdate = currentMillis;
    fetchAndDisplayData();
  }
  
  // Check WiFi connection periodically
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_WIFI, LOW);  // LED off = no WiFi
    displayNoWiFi();
    connectWiFi();
  } else {
    digitalWrite(LED_WIFI, HIGH);  // LED on = WiFi connected
  }
}

void connectWiFi() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Connecting to");
  display.println(ssid);
  display.display();
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    display.print(".");
    display.display();
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    display.clearDisplay();
    display.setCursor(0, 20);
    display.println("WiFi Connected!");
    display.print("IP: ");
    display.println(WiFi.localIP());
    display.display();
    delay(2000);
  } else {
    display.clearDisplay();
    display.setCursor(0, 20);
    display.println("WiFi Failed!");
    display.println("Check credentials");
    display.display();
    delay(3000);
  }
}

void displayStartup() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20, 20);
  display.println("CROWD");
  display.setCursor(35, 40);
  display.println("SENSE");
  display.display();
  delay(2000);
}

void displayNoWiFi() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("WiFi Lost!");
  display.println("Reconnecting...");
  display.display();
}

void fetchAndDisplayData() {
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
      const char* label = doc["label"] | "N/A";
      int count = doc["count"] | 0;
      const char* status = doc["status"] | "N/A";
      const char* destination = doc["destination"] | "N/A";
      
      displayResults(label, count, status, destination);
    } else {
      displayError("JSON Parse Error");
    }
  } else {
    displayError("Server Error: " + String(httpCode));
  }
  
  http.end();
}

void displayResults(const char* label, int count, const char* status, const char* destination) {
  display.clearDisplay();
  
  // Title
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Bus ");
  display.println(label);
  
  // Count - Big number
  display.setTextSize(4);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 20);
  display.print(count);
  
  // Status badge
  display.setTextSize(1);
  display.setCursor(75, 22);
  if (strcmp(status, "High") == 0) {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  } else if (strcmp(status, "Medium") == 0) {
    display.setTextColor(SSD1306_WHITE);
  } else {
    display.setTextColor(SSD1306_WHITE);
  }
  display.print(status);
  
  // Destination
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 52);
  display.setTextSize(1);
  display.print("To: ");
  display.println(destination);
  
  display.display();
}

void displayError(const char* errorMsg) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("ERROR:");
  display.println(errorMsg);
  display.display();
}
