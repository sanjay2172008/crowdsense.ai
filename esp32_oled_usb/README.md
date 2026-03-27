# ESP32 + OLED 0.96" + Traffic Signal LEDs (USB - No WiFi)

## Overview
This setup uses ESP32 connected to PC via USB cable with:
- **OLED Display** - Shows passenger count, bus info, arrival time
- **Traffic Signal LEDs** - Red/Yellow/Green to indicate crowd level

## Hardware Connections

### ESP32 to OLED (SSD1306 0.96" 128x64)
| ESP32 Pin | OLED Pin |
|-----------|----------|
| 3.3V      | VCC      |
| GND       | GND      |
| GPIO 21   | SDA      |
| GPIO 22   | SCL      |

### Traffic Signal LEDs
| ESP32 Pin | LED Color | Purpose |
|-----------|-----------|---------|
| GPIO 25   | RED LED   | High crowd - Don't go! |
| GPIO 26   | YELLOW LED | Medium crowd - Caution |
| GPIO 27   | GREEN LED | Low crowd - Safe to go |

### Optional: Status LED
| ESP32 Pin | Component |
|-----------|-----------|
| GPIO 2    | Built-in LED (Data indicator) |

### LED Connection (Each LED)
```
ESP32 GPIO ────[ 220Ω Resistor ]──── LED Anode (+)
GND ───────────────────────────────── LED Cathode (-)
```

### Traffic Light Module (If using module)
| ESP32 Pin | Module Pin |
|-----------|------------|
| GPIO 25   | R (Red)   |
| GPIO 26   | Y (Yellow)|
| GPIO 27   | G (Green) |
| GND       | GND       |

## How It Works

```
PC (runs Python) ← USB → ESP32 → OLED Display
                            ↓
                     Traffic LEDs
                            ↓
              [RED] = High crowd (Don't go!)
              [YELLOW] = Medium crowd (Caution)
              [GREEN] = Low crowd (Safe to go!)
```

## Software Setup

### 1. Arduino IDE - ESP32 Code
1. Open `esp32_display/esp32_display.ino` in Arduino IDE
2. Install libraries:
   - **Adafruit GFX Library**
   - **Adafruit SSD1306**
3. Select board: **ESP32 Arduino → DOIT ESP32 DEVKIT V1**
4. Select correct **Port**
5. Upload code

### 2. Python - PC Controller
1. Install Python dependencies:
   ```
   pip install pyserial requests
   ```
2. Connect ESP32 to PC via USB
3. Close Arduino IDE Serial Monitor
4. Run the controller:
   ```
   python pc_controller.py
   ```

## Usage

### Step 1: Update Configuration
Edit `pc_controller.py`:
```python
SERVER_URL = "https://your-app.railway.app"  # Your deployed URL
SERIAL_PORT = "COM5"  # Your ESP32 port
QUERY_PARAM = "q=12b"  # Bus query
```

### Step 2: Run
```bash
cd esp32_oled_usb/esp32_display
python pc_controller.py
```

## Display & LED Behavior

| Crowd Status | Traffic LED | OLED Badge | Meaning |
|--------------|-------------|------------|---------|
| HIGH         | 🔴 RED ON   | HIGH       | Crowded - Avoid |
| MEDIUM       | 🟡 YELLOW ON | MEDIUM     | Moderate - Go if needed |
| LOW          | 🟢 GREEN ON | LOW        | Safe - Good to go |

## LED Indicator Summary
- **LED ON = Data received from PC**
- **Traffic Light:**
  - 🔴 **Red** = High crowd (crowded)
  - 🟡 **Yellow** = Medium crowd (moderate)
  - 🟢 **Green** = Low crowd (safe)

## OLED Display Shows
- **Bus Number** (e.g., Bus 12B)
- **Passenger Count** (large number)
- **Crowd Status** (HIGH/MEDIUM/LOW)
- **Traffic Signal Indicator** (on screen)
- **Destination**
- **Next Arrival Time**

## Queries
Change `QUERY_PARAM` to display different data:

| Location | Query |
|----------|-------|
| Bus 12B | `q=12b` |
| Bus 5 | `q=5` |
| Apollo Hospital | `q=apollo` |
| Meenakshi Temple | `q=meenakshi` |

## Troubleshooting

### "Serial port not found"
1. Check USB cable is data cable
2. Check ESP32 port in Device Manager
3. Make sure Arduino IDE Serial Monitor is CLOSED

### LEDs not working
1. Check LED polarity (long leg = +)
2. Use 220Ω resistors for each LED
3. Check connections to GPIO 25, 26, 27

### OLED not showing anything
1. Check OLED connections (SDA→21, SCL→22)
2. Try OLED address 0x3D if 0x3C doesn't work
