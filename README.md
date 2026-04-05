# PicoTemperatureLogger
This is a MicroPython script that works on the raspberry pi pico to continuously record data and write to a csv file.
<img width="593" height="425" alt="image" src="https://github.com/user-attachments/assets/6c3c501a-4a15-4cdc-b015-4651fd67964a" />
# 📊 Raspberry Pi Pico Temperature Data Logger

A simple, low-cost temperature logging system built using a Raspberry Pi Pico (or Pico W) and a thermistor.
This project records temperature readings at regular intervals and saves them to a CSV file for later analysis.

---

Parts used:
* Raspberry Pi Pico or Pico W , same as Pi Pico 2 and 2W (wireless version optional) 
* Breadboard
* Thermistor (typically 10kΩ at 25°C)
* Fixed resistor (10kΩ recommended) this is what was used to develop program
* Jumper wires 3 M/M
* Optional:
  * LED (external, if not using onboard LED) might also need additional resistors...
  * Battery pack (to make it completely wireless)

---

# ⚙️ How It Works

1. The thermistor forms a voltage divider with a fixed resistor.
2. The Pico reads the voltage using its ADC (Analog-to-Digital Converter).
3. Temperature is calculated using the Beta equation.
4. Readings are saved to a file (`temps.csv`) stored on the Pico.
5. When plugged into a computer, the file can be downloaded and analysed (e.g. in Excel, or put into another program to plot it).

---

# Files in This Repository

* `main.py` → Non-wireless version (uses uptime for timestamps)
* `main_wireless.py` → Wireless version (uses WiFi to sync real time)

---

# Configuration

All important settings are near the top of each script.

### Thermistor Settings

```python
SERIES_RESISTOR = 10
NOMINAL_RESISTANCE = 10
B_COEFFICIENT = 3950
```

Adjust these if:

* You use a different thermistor
* You want more accurate readings

---

### ⏱️ Logging Interval

```python
time.sleep(59)
```

* Controls how often temperature is recorded
* Default = 60 seconds (1 minute)
* Change this to log faster/slower

---

### Time Offset (Wireless Version Only)

```python
time.time() + 3600
```

* Adjusts for timezone (UK example shown)
* Use:

  * `0` → GMT
  * `3600` → BST (summer time)

---

### 📶 WiFi Credentials (Wireless Version Only)

```python
SSID = "your_wifi"
PASSWORD = "your_password"
```

---

# Output File

The logger creates:

```
temps.csv
```

Example:

```
timestamp,temperature
2026-04-05 14:32:00,22.45
2026-04-05 14:33:00,22.51
```

You can:

* Download via Thonny
* Open in Excel / LibreOffice
* Plot graphs

---

# Running Without a Computer (Battery Mode)

This project can run completely standalone.

### Power Options

* USB power bank to just plug into micro usb-c
* 3x/2x AA battery pack for this plug the positive (normally red) into VSYS and the negative (normally black) into GND (there is one right under VSYS)

### Notes

* The Pico will start logging automatically on power **WHEN** the file is called "main.py" so if you get the wireless version rename it to "main.py" as when the pico recieves power it will run any file named "main.py"
* Data is saved to internal flash memory
* You can unplug it and retrieve the file later.

---

# Wireless vs Non-Wireless

| Feature         | main.py  | main_wireless.py         |
| --------------- | -------- | ------------------------ |
| WiFi required   | ❌       | ✅                       |
| Real timestamps | ❌       | ✅                       |
| Power usage     | Low      | Higher                   |

---


Feel free to modify and expand — that’s the whole point of the project

