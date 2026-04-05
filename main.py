import machine
from machine import Pin, ADC
import time
import math
import network
import ntptime

SSID = ""
PASSWORD = ""     


SERIES_RESISTOR = 10         # kΩ value of your fixed resistor
NOMINAL_RESISTANCE = 10      # kΩ thermistor resistance at 25°C
B_COEFFICIENT = 3950         # Beta coefficient of thermistor


adc = ADC(26) # GPIO pin used for thermistor (ADC0 = GP26)
led = Pin("LED", Pin.OUT) # Onboard LED if "LED" can change to seperate


def connect_wifi():
    """
    Connect to WiFi using provided SSID and PASSWORD.

    Returns:
        wlan (network.WLAN): Connected WLAN object

    Raises:
        RuntimeError: If connection fails within WIFI_TIMEOUT seconds

    Notes:
        - LED is ON while connecting
        - LED blinks rapidly if connection fails
        - Timeout duration can be adjusted via WIFI_TIMEOUT
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    led.on()  # Indicate connection attempt

    for _ in range(20):  # Seconds to wait for WiFi connection
        if wlan.isconnected():
            led.off()
            return wlan
        time.sleep(1)

    # Failed connection indication
    led.off()
    for _ in range(10):
        led.toggle()
        time.sleep(0.1)

    raise RuntimeError("WiFi connection failed")


def sync_time(wlan):
    """
    Synchronise system time using NTP, then disable WiFi to save power.

    Args:
        wlan (network.WLAN): Active WLAN connection

    Notes:
        - Uses ntptime (UTC time)
        - Applies no timezone automatically (handled separately)
        - WiFi is turned off after sync to reduce power usage
    """
    ntptime.settime()

    wlan.disconnect()
    wlan.active(False) # Automatically disconnects to conserve power if battery powered, see README


def read_temp():
    """
    Read temperature from thermistor using ADC and convert to Celsius.

    Returns:
        float: Temperature in degrees Celsius
        None: If voltage reading is invalid (e.g. divide-by-zero risk)

    Notes:
        - Uses Beta equation approximation
        - Assumes:
            * SERIES_RESISTOR (kΩ)
            * NOMINAL_RESISTANCE (kΩ at 25°C)
            * B_COEFFICIENT
        - Adjust constants in CONFIGURATION for better accuracy
    """
    adc_value = adc.read_u16()
    voltage = adc_value / 65535.0 * 3.3

    # Prevent division error if voltage saturates
    if voltage >= 3.3:
        return None

    # Calculate thermistor resistance
    Rt = SERIES_RESISTOR * voltage / (3.3 - voltage)

    # Apply Beta formula
    tempK = 1 / (
        1 / (273.15 + 25) +
        math.log(Rt / NOMINAL_RESISTANCE) / B_COEFFICIENT
    )

    return tempK - 273.15  # Convert to Celsius


def get_timestamp():
    """
    Generate formatted timestamp string adjusted for local timezone.

    Returns:
        str: Timestamp in format 'YYYY-MM-DD HH:MM:SS'

    Notes:
        - Uses UTC time from ntptime
        - Applies 1 manually depending on british summer or winter, can change according to location
        - Change UTC_OFFSET for timezone/DST handling
    """
    t = time.localtime(time.time() + 1)

    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


def init_log_file():
    """
    Create CSV log file if it does not already exist.

    File:
        temps.csv

    Notes:
        - Adds header row on first creation
        - Safe to call every boot
    """
    try:
        with open("temps.csv", "x") as f:
            f.write("timestamp,temperature\n")
    except:
        pass


def log_temperature(temp):
    """
    Append a temperature reading to the CSV log file.

    Args:
        temp (float): Temperature in Celsius

    Notes:
        - Values are rounded to 2 decimal places
        - File grows over time (consider rotation if long-term logging)
    """
    timestamp = get_timestamp()

    with open("temps.csv", "a") as f:
        f.write("{},{:.2f}\n".format(timestamp, temp))

    print(timestamp, temp)

wlan = connect_wifi()

# Visual confirmation of successful connection
for _ in range(3):
    led.toggle()
    time.sleep(0.5)
led.off()

sync_time(wlan)

init_log_file()

while True:
    temp = read_temp()

    if temp is not None:
        log_temperature(temp)

    # LED blink to indicate logging event, can be removed
    led.toggle()
    time.sleep(1)
    led.toggle()

    time.sleep(59) # Time between temperature readings (seconds)
