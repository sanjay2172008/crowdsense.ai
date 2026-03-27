#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED Configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Traffic Signal LEDs
#define LED_RED    25
#define LED_YELLOW 26
#define LED_GREEN  27

// Buttons
#define BTN_RED    34
#define BTN_YELLOW 35
#define BTN_GREEN  32

// Data
String busLabel = "MANUAL";
int passengerCount = 0;
String crowdStatus = "LOW";
String destination = "TEST";
String nextArrival = "---";

void setup() {
  Serial.begin(115200);
  
  // LED pins
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  
  // Button pins (pullup)
  pinMode(BTN_RED, INPUT_PULLUP);
  pinMode(BTN_YELLOW, INPUT_PULLUP);
  pinMode(BTN_GREEN, INPUT_PULLUP);
  
  allLEDsOff();
  
  // OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  
  displayStartup();
  showHelp();
  
  setStatus("LOW");
}

void loop() {
  // Check buttons
  if (digitalRead(BTN_RED) == LOW) {
    setStatus("HIGH");
    delay(300);
  }
  if (digitalRead(BTN_YELLOW) == LOW) {
    setStatus("MEDIUM");
    delay(300);
  }
  if (digitalRead(BTN_GREEN) == LOW) {
    setStatus("LOW");
    delay(300);
  }
  
  // Check serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();
    
    if (cmd == "RED" || cmd == "R" || cmd == "HIGH") {
      setStatus("HIGH");
    } else if (cmd == "YELLOW" || cmd == "Y" || cmd == "MEDIUM") {
      setStatus("MEDIUM");
    } else if (cmd == "GREEN" || cmd == "G" || cmd == "LOW") {
      setStatus("LOW");
    } else if (cmd.startsWith("COUNT:")) {
      passengerCount = cmd.substring(6).toInt();
      updateDisplay();
    } else if (cmd.startsWith("BUS:")) {
      busLabel = cmd.substring(4);
      updateDisplay();
    } else if (cmd.startsWith("DEST:")) {
      destination = cmd.substring(5);
      if (destination.length() > 12) destination = destination.substring(0, 12);
      updateDisplay();
    } else if (cmd.startsWith("ARRIVE:")) {
      nextArrival = cmd.substring(7);
      updateDisplay();
    } else if (cmd == "HELP" || cmd == "H" || cmd == "?") {
      showHelp();
    } else if (cmd == "CLEAR" || cmd == "CLS") {
      display.clearDisplay();
      display.display();
    } else if (cmd == "OFF") {
      allLEDsOff();
      Serial.println("All LEDs OFF");
    } else {
      Serial.println("Unknown command. Type HELP");
    }
  }
}

void showHelp() {
  Serial.println("========================================");
  Serial.println("  MANUAL CONTROL - Type commands:");
  Serial.println("========================================");
  Serial.println("  RED / R / HIGH   = Red LED ON");
  Serial.println("  YELLOW / Y      = Yellow LED ON");
  Serial.println("  GREEN / G / LOW  = Green LED ON");
  Serial.println("  OFF              = All LEDs OFF");
  Serial.println("  COUNT:25         = Set passenger count");
  Serial.println("  BUS:12B          = Set bus number");
  Serial.println("  DEST:Chennai      = Set destination");
  Serial.println("  ARRIVE:5 mins    = Set arrival time");
  Serial.println("  HELP / H         = Show this help");
  Serial.println("  CLEAR            = Clear OLED");
  Serial.println("========================================");
  Serial.println("  Or use BUTTONS:");
  Serial.println("  GPIO34 = RED, GPIO35 = YELLOW, GPIO32 = GREEN");
  Serial.println("========================================");
}

void setStatus(String status) {
  crowdStatus = status;
  allLEDsOff();
  
  if (status == "HIGH") {
    digitalWrite(LED_RED, HIGH);
    Serial.println(">>> RED LED - HIGH CROWD");
  } else if (status == "MEDIUM") {
    digitalWrite(LED_YELLOW, HIGH);
    Serial.println(">>> YELLOW LED - MEDIUM CROWD");
  } else if (status == "LOW") {
    digitalWrite(LED_GREEN, HIGH);
    Serial.println(">>> GREEN LED - LOW CROWD");
  }
  
  updateDisplay();
}

void allLEDsOff() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
}

void updateDisplay() {
  display.clearDisplay();
  
  // Header
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Bus ");
  display.println(busLabel);
  
  // Count
  display.setTextSize(4);
  display.setCursor(10, 18);
  display.print(passengerCount);
  
  // Status
  display.setTextSize(1);
  display.setCursor(75, 18);
  if (crowdStatus == "HIGH") {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    display.print(" HIGH ");
  } else if (crowdStatus == "MEDIUM") {
    display.setTextColor(SSD1306_WHITE);
    display.print("MEDIUM");
  } else {
    display.setTextColor(SSD1306_WHITE);
    display.print(" LOW  ");
  }
  
  // Destination
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 45);
  display.print("To: ");
  display.println(destination);
  
  // Arrival
  display.setCursor(0, 55);
  display.print("Next: ");
  display.print(nextArrival);
  
  display.display();
}

void displayStartup() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20, 15);
  display.println("MANUAL");
  display.setCursor(35, 35);
  display.println("MODE");
  display.setCursor(15, 52);
  display.setTextSize(1);
  display.println("Type HELP for commands");
  display.display();
  delay(2000);
}
