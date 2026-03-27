# ESP32 + OLED 0.96" Display (USB - No WiFi)

## Overview
This setup uses ESP32 connected to PC via USB cable. A Python script on PC fetches data from your deployed app and sends it to ESP32 via serial.

## Hardware Connections

### ESP32 to OLED (SSD1306 0.96" 128x64)
| ESP32 Pin | OLED Pin |
|-----------|----------|
| 3.3V      | VCC      |
| GND       | GND      |
| GPIO 21   | SDA      |
| GPIO 22   | SCL      |

### Status LED (Optional)
| ESP32 Pin | LED + 220Ω Resistor |
|-----------|---------------------|
| GPIO 2    | LED Anode (+)       |
| GND       | LED Cathode (-)     |

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
1. Install Python 3.x
2. Install required packages:
   ```
   pip install pyserial requests
   ```
3. Connect ESP32 to PC via USB
4. Close Arduino IDE Serial Monitor (important!)
5. Run the controller:
   ```
   python pc_controller.py
   ```

## Usage

### Step 1: Update Configuration
Before running, edit `pc_controller.py`:
```python
SERVER_URL = "https://your-app.railway.app"  # Your deployed URL
SERIAL_PORT = "COM5"  # Your ESP32 port
QUERY_PARAM = "q=12b"  # Bus/Hospital/Temple query
```

### Step 2: Run
```bash
cd esp32_oled_usb/esp32_display
python pc_controller.py
```

### Step 3: View on OLED
The OLED will display:
- **Bus Number** (e.g., Bus 12B)
- **Passenger Count** (big number)
- **Crowd Status** (HIGH/MEDIUM/LOW)
- **Destination**
- **Next Arrival Time**

## LED Indicator
- **LED ON** = Data received from PC
- **LED OFF** = No data / timeout

## Queries
Change `QUERY_PARAM` to display different data:

| Location | Query |
|----------|-------|
| Bus 12B | `q=12b` |
| Bus 5 | `q=5` |
| Apollo Hospital | `q=apollo` |
| Meenakshi Temple | `q=meenakshi` |
| Fortis Hospital | `q=fortis` |

## Troubleshooting

### "Serial port not found"
1. Check USB cable is data cable (not charging only)
2. Check ESP32 port in Device Manager (Windows)
3. Make sure Arduino IDE Serial Monitor is CLOSED

### "Network error"
1. Check your deployed app URL is correct
2. Make sure app is deployed and running
3. Test URL in browser first

### OLED not showing anything
1. Check OLED connections (SDA→21, SCL→22)
2. Check OLED address is 0x3C (some are 0x3D)
3. Try reversing SDA/SCL wires

## Customization

### Change OLED Address
If your OLED uses 0x3D, change in code:
```cpp
if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3D))  // Change to 0x3D
```

### Change Pin Numbers
```cpp
#define OLED_SDA 21  // Change SDA pin
#define OLED_SCL 22  // Change SCL pin
```

### Change Update Interval
In `pc_controller.py`:
```python
UPDATE_INTERVAL = 5  # seconds
```
