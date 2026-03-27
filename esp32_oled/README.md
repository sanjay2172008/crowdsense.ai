# ESP32 + OLED Crowd Display Setup

## Hardware Connections

### ESP32 to OLED (SSD1306 128x64)
| ESP32 Pin | OLED Pin |
|-----------|----------|
| 3.3V      | VCC      |
| GND       | GND      |
| GPIO 21   | SDA      |
| GPIO 22   | SCL      |

### Optional: Status LED
| ESP32 Pin | LED      |
|-----------|----------|
| GPIO 2    | + (through 220Ω resistor) |
| GND       | -        |

## Software Setup

### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### 2. Add ESP32 Board Support
1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to "Additional Board Manager URLs":
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Go to **Tools → Board → Board Manager**
5. Search "ESP32" and install

### 3. Install Required Libraries
**Sketch → Include Library → Manage Libraries**
Install these:
- **WiFi** (built-in for ESP32)
- **ArduinoJson** by Benoit Blanchon
- **Adafruit GFX Library** by Adafruit
- **Adafruit SSD1306** by Adafruit
- **Adafruit BusIO** (dependency)

### 4. Configure the Code

Open `esp32_oled.ino` and change these lines:

```cpp
// CHANGE THESE TO YOUR WIFI CREDENTIALS
const char* ssid = "YOUR_WIFI_NAME";           // <-- Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // <-- Your WiFi password

// CHANGE THIS TO YOUR DEPLOYED APP URL
const char* serverUrl = "https://your-app.railway.app";  // <-- Your deployed URL

// Change query to search for:
// Bus:      const char* queryParam = "q=12b";
// Hospital: const char* queryParam = "q=apollo";
// Temple:   const char* queryParam = "q=meenakshi";
```

### 5. Upload to ESP32
1. Select Board: **Tools → Board → ESP32 Arduino → DOIT ESP32 DEVKIT V1**
2. Select Port: **Tools → Port → COMX** (or /dev/ttyUSB0)
3. Click **Upload** (→)

## WiFi Troubleshooting

### If WiFi won't connect:
1. Make sure WiFi name/password is correct (no special characters)
2. Make sure WiFi is 2.4GHz (not 5GHz)
3. Try moving ESP32 closer to router
4. Check Serial Monitor for error messages

### Serial Monitor
Open **Tools → Serial Monitor** (115200 baud) to see debug messages.

## After Setup
- ESP32 will display "CrowdSense" on startup
- Connect to WiFi (LED on = connected)
- Show passenger count, status, and destination
- Auto-refresh every 10 seconds
