# ESP32 + OLED + LEDs - MANUAL CONTROL

## No WiFi, No PC Script Needed!

Control OLED display and LEDs by typing commands in Serial Monitor or using buttons!

## Hardware

### ESP32 to OLED
| ESP32 | OLED |
|-------|------|
| 3.3V | VCC |
| GND | GND |
| GPIO 21 | SDA |
| GPIO 22 | SCL |

### LEDs
| ESP32 | LED |
|-------|-----|
| GPIO 25 | 🔴 RED |
| GPIO 26 | 🟡 YELLOW |
| GPIO 27 | 🟢 GREEN |

### Buttons (Optional)
| ESP32 | Button |
|-------|--------|
| GPIO 34 | RED Button |
| GPIO 35 | YELLOW Button |
| GPIO 32 | GREEN Button |

## Commands (Type in Serial Monitor)

| Command | Action |
|---------|--------|
| `RED` or `R` | Red LED ON |
| `YELLOW` or `Y` | Yellow LED ON |
| `GREEN` or `G` | Green LED ON |
| `OFF` | All LEDs OFF |
| `COUNT:25` | Set passenger count to 25 |
| `BUS:12B` | Set bus number to 12B |
| `DEST:Chennai` | Set destination |
| `ARRIVE:5 mins` | Set arrival time |
| `HELP` | Show all commands |
| `CLEAR` | Clear OLED screen |

## Examples

```
COUNT:45       → Shows 45 passengers
BUS:5A         → Shows "Bus 5A"
DEST:Airport   → Shows destination
ARRIVE:3 mins  → Shows arrival time
RED            → Red LED ON
GREEN          → Green LED ON
```

## Buttons
- Press RED button → Red LED ON
- Press YELLOW button → Yellow LED ON  
- Press GREEN button → Green LED ON

## No Setup Needed!
- No WiFi
- No Flask app
- No Python script
- Just upload and use!
