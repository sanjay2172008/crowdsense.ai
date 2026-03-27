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

// Traffic Signal LEDs
#define LED_RED    25   // GPIO 25 - Red LED (High crowd)
#define LED_YELLOW 26   // GPIO 26 - Yellow LED (Medium crowd)
#define LED_GREEN  27   // GPIO 27 - Green LED (Low crowd)
#define LED_STATUS 2    // Built-in LED (Data indicator)

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
    Serial.println("OLED failed");
    while(1);
  }
  
  displayStartup();
}

void loop() {
  // Check for serial data from PC
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (data.length() > 0) {
      parseData(data);
      dataReceived = true;
      lastUpdate = millis();
      digitalWrite(LED_STATUS, HIGH);
      updateTrafficLEDs();
      displayResults();
    }
  }
  
  // Check timeout
  if (dataReceived && (millis() - lastUpdate > timeout)) {
    displayWaiting();
    allLEDsOff();
    dataReceived = false;
  }
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

void displayWaiting() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 20);
  display.println("Waiting for");
  display.println("PC Connection...");
  display.println("");
  display.print("Baud: 115200");
  display.display();
  digitalWrite(LED_STATUS, LOW);
}

void parseData(String data) {
  // Format: "BUS:12B,COUNT:25,STATUS:Medium,DEST:Thiruvanmiyur,ARRIVE:5 mins"
  
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
  
  // Status Badge
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
  display.println(destination);
  
  // Next Arrival
  display.setCursor(0, 55);
  display.print("Next: ");
  display.print(nextArrival);
  
  display.display();
}
