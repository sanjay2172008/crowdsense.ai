# ESP32 + OLED 0.96" + Traffic LEDs (USB - No WiFi)

## Overview
ESP32 connected to PC via USB. PC fetches data from deployed app and sends to ESP32.
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
| GPIO 2    | Built-in LED | Data indicator |

### LED Connection (Each LED)
```
ESP32 GPIO 25/26/27 ────[ 220Ω Resistor ]──── LED Anode (+)
GND ─────────────────────────────────────────── LED Cathode (-)
```

## How It Works

```
PC (runs Python) ← USB → ESP32 → OLED Display
                            ↓
                     Traffic LEDs
                            ↓
              [RED] = High crowd (Don't go!)
              [YELLOW] = Medium crowd (Caution)
              [GREEN] = Low crowd (Safe!)

PC → Deployed App → Crowd Data → PC → ESP32
```

## Software Setup

### 1. Arduino IDE - ESP32 Code
1. Open `esp32_usb/esp32_usb.ino` in Arduino IDE
2. Install libraries:
   - **Adafruit GFX Library**
   - **Adafruit SSD1306**
3. Select board: **ESP32 Arduino → DOIT ESP32 DEVKIT V1**
4. Select correct **Port**
5. Upload code

### 2. Python - PC Controller
1. Install Python dependencies:
   ```bash
   pip install pyserial requests
   ```
2. Connect ESP32 to PC via USB
3. **CLOSE Arduino IDE Serial Monitor**
4. Run:
   ```bash
   python pc_controller.py
   ```

## Configuration

Before running, edit `pc_controller.py`:
```python
SERVER_URL = "https://your-app.railway.app"  # Your deployed URL
SERIAL_PORT = "COM5"  # Your ESP32 port
QUERY_PARAM = "q=12b"  # Bus/Hospital/Temple query
```

## What Shows

### OLED Display:
- **Bus Number** (e.g., Bus 12B)
- **Passenger Count** (large number)
- **Crowd Status** (HIGH/MEDIUM/LOW)
- **Destination**
- **Next Arrival Time**

### Traffic LEDs:
| Crowd Status | LED ON | Meaning |
|--------------|--------|---------|
| **HIGH** | 🔴 RED | Crowded - Don't go! |
| **MEDIUM** | 🟡 YELLOW | Moderate - Be careful |
| **LOW** | 🟢 GREEN | Safe - Go! |

### Status LED (GPIO 2):
- **LED ON** = Data received from PC

## Queries
| Location | Query |
|----------|-------|
| Bus 12B | `q=12b` |
| Bus 5 | `q=5` |
| Apollo Hospital | `q=apollo` |
| Meenakshi Temple | `q=meenakshi` |

## Troubleshooting

### "Serial port not found"
1. Check USB cable is data cable (not charging only)
2. Check ESP32 port in Device Manager
3. Make sure Arduino IDE Serial Monitor is CLOSED

### "Network error"
1. Check your deployed app URL is correct
2. Make sure app is deployed and running
3. Test URL in browser first

### OLED not showing anything
1. Check OLED connections (SDA→21, SCL→22)
2. Try OLED address 0x3D if 0x3C doesn't work

### LEDs not working
1. Check LED polarity (long leg = +)
2. Use 220Ω resistors for each LED

## Benefits of USB Setup
- No WiFi configuration needed
- More stable connection
- Can use any WiFi network on PC
- ESP32 is simpler (no WiFi library needed)
