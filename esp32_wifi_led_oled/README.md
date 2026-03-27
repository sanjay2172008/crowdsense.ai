# ESP32 + OLED 0.96" + Traffic LEDs (WiFi - Standalone)

## Overview
ESP32 connects to WiFi and fetches crowd data from your deployed app.
Shows results on **BOTH** OLED display and **Traffic LEDs**.

## Hardware Connections

### ESP32 to OLED (SSD1306 0.96" 128x64)
| ESP32 Pin | OLED Pin |
|-----------|----------|
| 3.3V      | VCC      |
| GND       | GND      |
| GPIO 21   | SDA      |
| GPIO 22   | SCL      |

### Traffic Signal LEDs
| ESP32 Pin | LED Color | Meaning |
|-----------|-----------|---------|
| GPIO 25   | 🔴 RED LED | High crowd - Don't go! |
| GPIO 26   | 🟡 YELLOW LED | Medium crowd - Caution |
| GPIO 27   | 🟢 GREEN LED | Low crowd - Safe! |
| GPIO 2    | Built-in LED | WiFi status |

### LED Connection (Each LED)
```
ESP32 GPIO 25/26/27 ────[ 220Ω Resistor ]──── LED Anode (+)
GND ─────────────────────────────────────────── LED Cathode (-)
```

## Software Setup

### 1. Install Arduino ESP32 Board
1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add URL: `https://dl.espressif.com/dl/package_esp32_index.json`
4. **Tools → Board → Board Manager** → Install "ESP32"

### 2. Install Libraries
**Sketch → Include Library → Manage Libraries**
Install:
- **ArduinoJson** by Benoit Blanchon
- **Adafruit GFX Library** by Adafruit
- **Adafruit SSD1306** by Adafruit

### 3. Configure Code
Edit these lines in `esp32_wifi.ino`:
```cpp
// CHANGE THESE TO YOUR WIFI CREDENTIALS
const char* ssid = "YOUR_WIFI_NAME";           // Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";     // Your WiFi password

// CHANGE THIS TO YOUR DEPLOYED APP URL
const char* serverUrl = "https://your-app.railway.app";  // Your URL

// What to display
const char* queryParam = "q=12b";  // q=12b (bus), q=apollo (hospital), q=meenakshi (temple)
```

### 4. Upload
1. Select Board: **Tools → Board → ESP32 Arduino → DOIT ESP32 DEVKIT V1**
2. Select Port
3. Upload!

## How It Works

```
ESP32 ──WiFi──> Your Deployed App ──> Crowd Data
    │
    ├──> OLED Display (Bus, Count, Status, Destination, Arrival)
    │
    └──> Traffic LEDs (Red/Yellow/Green based on crowd)
```

## What Shows on Display

### OLED Shows:
- **Bus Number** (e.g., Bus 12B)
- **Passenger Count** (large number)
- **Crowd Status** (HIGH/MEDIUM/LOW)
- **Destination**
- **Next Arrival Time**

### Traffic LEDs Show:
| Crowd Status | LED ON | Meaning |
|--------------|--------|---------|
| **HIGH** | 🔴 RED | Crowded - Don't go! |
| **MEDIUM** | 🟡 YELLOW | Moderate - Be careful |
| **LOW** | 🟢 GREEN | Safe - Go! |

### Status LED (GPIO 2):
- **ON** = WiFi connected
- **OFF** = No WiFi

## LED Error Pattern
If there's an error, all LEDs blink 3 times.

## Queries
| Location | Query |
|----------|-------|
| Bus 12B | `q=12b` |
| Bus 5 | `q=5` |
| Apollo Hospital | `q=apollo` |
| Fortis Hospital | `q=fortis` |
| Meenakshi Temple | `q=meenakshi` |
| Tirupati | `q=tirupati` |

## Troubleshooting

### WiFi won't connect?
1. Check WiFi name & password are correct
2. Make sure WiFi is 2.4GHz (not 5GHz)
3. Move ESP32 closer to router

### Check Serial Monitor
Open **Tools → Serial Monitor** (115200 baud) to see debug messages.

### OLED not showing?
1. Check OLED connections (SDA→21, SCL→22)
2. Try OLED address 0x3D if 0x3C doesn't work

### LEDs not working?
1. Check LED polarity (long leg = +)
2. Use 220Ω resistors for each LED
