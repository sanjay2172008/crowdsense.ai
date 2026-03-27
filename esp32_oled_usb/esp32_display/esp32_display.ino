#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED Configuration (0.96 inch - 128x64)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// LED indicator
#define LED_STATUS 2

// Data variables
String busLabel = "---";
int passengerCount = 0;
String crowdStatus = "---";
String destination = "---";
String nextArrival = "---";

bool dataReceived = false;
unsigned long lastUpdate = 0;
const unsigned long timeout = 5000;  // 5 second timeout if no data

void setup() {
  Serial.begin(115200);
  
  // Initialize LED
  pinMode(LED_STATUS, OUTPUT);
  digitalWrite(LED_STATUS, LOW);
  
  // Initialize OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED failed");
    while(1);
  }
  
  displayStartup();
}

void loop() {
  // Check for serial data
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (data.length() > 0) {
      parseData(data);
      dataReceived = true;
      lastUpdate = millis();
      digitalWrite(LED_STATUS, HIGH);  // LED on = data received
    }
  }
  
  // Check timeout
  if (dataReceived && (millis() - lastUpdate > timeout)) {
    displayTimeout();
    dataReceived = false;
  }
  
  // Always update display with current data
  displayData();
}

void displayStartup() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 15);
  display.println("CROWD");
  display.setCursor(25, 35);
  display.println("SENSE");
  display.setCursor(15, 52);
  display.setTextSize(1);
  display.println("AI System Ready");
  display.display();
  delay(2000);
}

void displayTimeout() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 25);
  display.println("Waiting for");
  display.println("PC Connection...");
  display.println("");
  display.print("Baud: 115200");
  display.display();
  digitalWrite(LED_STATUS, LOW);
}

void parseData(String data) {
  // Format: "BUS:12B,COUNT:25,STATUS:Medium,DEST:Thiruvanmiyur,ARRIVE:5 mins"
  // Or any subset of this format
  
  int busIdx = data.indexOf("BUS:");
  int countIdx = data.indexOf("COUNT:");
  int statusIdx = data.indexOf("STATUS:");
  int destIdx = data.indexOf("DEST:");
  int arriveIdx = data.indexOf("ARRIVE:");
  
  if (busIdx >= 0) {
    int start = busIdx + 4;
    int end = data.indexOf(",", start);
    if (end < 0) end = data.length();
    busLabel = data.substring(start, end);
  }
  
  if (countIdx >= 0) {
    int start = countIdx + 6;
    int end = data.indexOf(",", start);
    if (end < 0) end = data.length();
    passengerCount = data.substring(start, end).toInt();
  }
  
  if (statusIdx >= 0) {
    int start = statusIdx + 7;
    int end = data.indexOf(",", start);
    if (end < 0) end = data.length();
    crowdStatus = data.substring(start, end);
  }
  
  if (destIdx >= 0) {
    int start = destIdx + 5;
    int end = data.indexOf(",", start);
    if (end < 0) end = data.length();
    destination = data.substring(start, end);
    if (destination.length() > 15) {
      destination = destination.substring(0, 12) + "...";
    }
  }
  
  if (arriveIdx >= 0) {
    int start = arriveIdx + 7;
    int end = data.indexOf(",", start);
    if (end < 0) end = data.length();
    nextArrival = data.substring(start, end);
  }
}

void displayData() {
  display.clearDisplay();
  
  // Header - Bus Number
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Bus ");
  display.println(busLabel);
  
  // Big Count Number
  display.setTextSize(5);
  display.setCursor(5, 18);
  display.print(passengerCount);
  
  // Status Badge (right side)
  display.setTextSize(1);
  display.setCursor(80, 18);
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
  display.setCursor(0, 48);
  display.print("To: ");
  display.println(destination);
  
  // Arrival Time
  display.setCursor(0, 56);
  display.print("Next: ");
  display.print(nextArrival);
  
  display.display();
}
