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
const char* queryParam = "q=12b";  // q=12b (bus), q=apollo (hospital), q=meenakshi (temple)
// ==========================================

// OLED Configuration (0.96 inch - 128x64)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Traffic Signal LEDs
#define LED_RED    25   // GPIO 25 - Red LED (High crowd)
#define LED_YELLOW 26   // GPIO 26 - Yellow LED (Medium crowd)
#define LED_GREEN  27   // GPIO 27 - Green LED (Low crowd)
#define LED_STATUS 2    // Built-in LED (WiFi status)

// Update interval (milliseconds)
const long updateInterval = 10000;  // Update every 10 seconds
unsigned long previousUpdate = 0;

// Data variables
String busLabel = "---";
int passengerCount = 0;
String crowdStatus = "---";
String destination = "---";
String nextArrival = "---";

void setup() {
  Serial.begin(115200);
  
  // Initialize LED pins
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  
  // All LEDs off initially
  allLEDsOff();
  
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
  
  // Update data every interval
  if (currentMillis - previousUpdate >= updateInterval) {
    previousUpdate = currentMillis;
    fetchAndDisplayData();
  }
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_STATUS, LOW);
    displayNoWiFi();
    connectWiFi();
  } else {
    digitalWrite(LED_STATUS, HIGH);  // LED on = WiFi connected
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
    fetchAndDisplayData();  // Get initial data
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
  display.setCursor(20, 15);
  display.println("CROWD");
  display.setCursor(35, 35);
  display.println("SENSE");
  display.setCursor(15, 52);
  display.setTextSize(1);
  display.println("AI System Ready");
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
  allLEDsOff();
}

void allLEDsOff() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
}

void updateTrafficLEDs() {
  allLEDsOff();
  
  if (crowdStatus == "High") {
    digitalWrite(LED_RED, HIGH);
    Serial.println(">>> RED LED ON - HIGH CROWD");
  } 
  else if (crowdStatus == "Medium") {
    digitalWrite(LED_YELLOW, HIGH);
    Serial.println(">>> YELLOW LED ON - MEDIUM CROWD");
  } 
  else if (crowdStatus == "Low") {
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

void fetchAndDisplayData() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 25);
  display.println("Fetching data...");
  display.display();
  
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
      busLabel = doc["label"] | "---";
      passengerCount = doc["count"] | 0;
      crowdStatus = doc["status"] | "---";
      destination = doc["destination"] | "---";
      nextArrival = doc["next_arrival"] | "---";
      
      updateTrafficLEDs();
      displayResults();
    } else {
      displayError("JSON Parse Error");
      blinkAllLEDsError();
    }
  } else {
    displayError("Server Error: " + String(httpCode));
    blinkAllLEDsError();
  }
  
  http.end();
}

void displayResults() {
  display.clearDisplay();
  
  // Header - Bus Number
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Bus ");
  display.println(busLabel);
  
  // Big Count Number
  display.setTextSize(4);
  display.setCursor(10, 18);
  display.print(passengerCount);
  
  // Traffic Light on Display
  display.setTextSize(1);
  display.setCursor(75, 18);
  if (crowdStatus == "High") {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    display.print(" HIGH ");
  } else if (crowdStatus == "Medium") {
    display.setTextColor(SSD1306_WHITE);
    display.print("MEDIUM");
  } else if (crowdStatus == "Low") {
    display.setTextColor(SSD1306_WHITE);
    display.print(" LOW  ");
  } else {
    display.setTextColor(SSD1306_WHITE);
    display.print(crowdStatus);
  }
  
  // Destination
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 45);
  display.print("To: ");
  if (destination.length() > 15) {
    display.println(destination.substring(0, 12) + "...");
  } else {
    display.println(destination);
  }
  
  // Next Arrival
  display.setCursor(0, 55);
  display.print("Next: ");
  display.print(nextArrival);
  
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
