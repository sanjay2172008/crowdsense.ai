"""
CrowdSense AI - ESP32 Display Controller
This script fetches data from the deployed app and sends to ESP32 via USB
"""

import serial
import time
import requests
import sys

# ============== CONFIGURATION ==============
# Change this to your deployed app URL
SERVER_URL = "https://your-app.railway.app"  # <-- CHANGE THIS

# Serial port (change to match your ESP32)
# Windows: COM3, COM4, etc.
# Linux/Mac: /dev/ttyUSB0, /dev/ttyACM0, etc.
SERIAL_PORT = "COM5"  # <-- CHANGE THIS (check Arduino IDE Port)
BAUD_RATE = 115200

# What to display
QUERY_PARAM = "q=12b"  # Bus: q=12b, Hospital: q=apollo, Temple: q=meenakshi
UPDATE_INTERVAL = 5  # seconds

# =========================================

def find_serial_port():
    """Find available serial ports"""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    return ports

def connect_serial():
    """Connect to ESP32 via serial"""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        time.sleep(2)  # Wait for ESP32 to reset
        return ser
    except Exception as e:
        print(f"Serial Error: {e}")
        return None

def fetch_bus_data(bus_query):
    """Fetch crowd data from deployed app"""
    try:
        url = f"{SERVER_URL}/api/bus?{bus_query}"
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "bus": data.get("label", "---"),
                "count": data.get("count", 0),
                "status": data.get("status", "---"),
                "destination": data.get("destination", "---"),
                "arrival": data.get("next_arrival", "---")
            }
        else:
            print(f"Server error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

def send_to_esp32(ser, data):
    """Send data to ESP32 via serial"""
    if data:
        # Format: BUS:XX,COUNT:N,STATUS:XXX,DEST:XXX,ARRIVE:XXX
        message = f"BUS:{data['bus']},COUNT:{data['count']},STATUS:{data['status']},DEST:{data['destination']},ARRIVE:{data['arrival']}\n"
        
        try:
            ser.write(message.encode())
            print(f"Sent to ESP32: {message.strip()}")
            return True
        except Exception as e:
            print(f"Serial write error: {e}")
            return False
    return False

def main():
    print("=" * 50)
    print("  CrowdSense AI - ESP32 Display Controller")
    print("=" * 50)
    
    # Find available ports
    print("\nAvailable serial ports:")
    find_serial_port()
    
    # Allow manual port selection
    global SERIAL_PORT
    port_input = input(f"\nEnter serial port [{SERIAL_PORT}]: ").strip()
    if port_input:
        SERIAL_PORT = port_input
    
    # Allow server URL input
    global SERVER_URL
    url_input = input(f"Enter server URL [{SERVER_URL}]: ").strip()
    if url_input:
        SERVER_URL = url_input
    
    # Allow query input
    global QUERY_PARAM
    query_input = input(f"Enter query [{QUERY_PARAM}]: ").strip()
    if query_input:
        QUERY_PARAM = query_input
    
    print("\n" + "=" * 50)
    print(f"  Server: {SERVER_URL}")
    print(f"  Query:  {QUERY_PARAM}")
    print(f"  Port:   {SERIAL_PORT}")
    print("=" * 50)
    
    # Connect to ESP32
    ser = connect_serial()
    if not ser:
        print("Failed to connect to ESP32. Make sure:")
        print("  1. ESP32 is connected via USB")
        print("  2. Correct port is selected")
        print("  3. Arduino IDE Serial Monitor is CLOSED")
        sys.exit(1)
    
    print("\nFetching data and sending to ESP32...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            data = fetch_bus_data(QUERY_PARAM)
            if data:
                send_to_esp32(ser, data)
            else:
                print("Failed to fetch data")
            
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser:
            ser.close()
            print("Serial port closed")

if __name__ == "__main__":
    main()
