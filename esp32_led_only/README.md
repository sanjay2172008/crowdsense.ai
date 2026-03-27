# ESP32 + Traffic Signal LEDs (WiFi - Standalone)

## Overview
ESP32 connects to WiFi and fetches crowd data from your deployed app.
Only **Traffic Signal LEDs** are used - no OLED display.

## Hardware Connections

### Traffic Signal LEDs (or Traffic Light Module)
| ESP32 Pin | LED | Meaning |
|-----------|-----|---------|
| GPIO 25 | 🔴 RED LED | High crowd - Don't go! |
| GPIO 26 | 🟡 YELLOW LED | Medium crowd - Caution |
| GPIO 27 | 🟢 GREEN LED | Low crowd - Safe! |
| GPIO 2 | Built-in LED | WiFi status |

### LED Connection (Each LED needs resistor!)
```
ESP32 GPIO 25/26/27 ────[ 220Ω Resistor ]──── LED Anode (+)
GND ─────────────────────────────────────────── LED Cathode (-)
```

### Using Traffic Light Module
| ESP32 Pin | Module Pin |
|-----------|------------|
| GPIO 25 | R (Red) |
| GPIO 26 | Y (Yellow) |
| GPIO 27 | G (Green) |
| GND | GND |

## Software Setup

### 1. Install Arduino ESP32 Board
1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add URL: `https://dl.espressif.com/dl/package_esp32_index.json`
4. **Tools → Board → Board Manager** → Install "ESP32"

### 2. Install Library
**Sketch → Include Library → Manage Libraries**
Install: **ArduinoJson** by Benoit Blanchon

### 3. Configure Code
Edit these lines in `esp32_led.ino`:
```cpp
const char* ssid = "YOUR_WIFI_NAME";           // Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password
const char* serverUrl = "https://your-app.railway.app";  // Your deployed URL
const char* queryParam = "q=12b";             // q=12b (bus), q=apollo, q=meenakshi
```

### 4. Upload
1. Select Board: **Tools → Board → ESP32 Arduino → DOIT ESP32 DEVKIT V1**
2. Select Port
3. Upload!

## LED Behavior

| Crowd Status | LED ON | Meaning |
|--------------|--------|---------|
| **HIGH** | 🔴 RED | Crowded - Avoid! |
| **MEDIUM** | 🟡 YELLOW | Moderate - Be careful |
| **LOW** | 🟢 GREEN | Safe - Good to go! |

## Status LED (GPIO 2)
- **ON** = WiFi connected
- **Blinking** = Connecting to WiFi
- **OFF** = No WiFi

## LED Error Pattern
If there's an error, all LEDs blink 3 times.

## Queries
| Location | Query |
|----------|-------|
| Bus 12B | `q=12b` |
| Bus 5 | `q=5` |
| Apollo Hospital | `q=apollo` |
| Meenakshi Temple | `q=meenakshi` |

## Troubleshooting

### WiFi won't connect?
1. Check WiFi name & password are correct
2. Make sure WiFi is 2.4GHz (not 5GHz)
3. Move ESP32 closer to router

### Check Serial Monitor
Open **Tools → Serial Monitor** (115200 baud) to see debug messages.
