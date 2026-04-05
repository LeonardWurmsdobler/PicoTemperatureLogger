from machine import Pin, ADC
import time
import math
import network
import ntptime

# WiFi credentials
SSID = ""
PASSWORD = ""

# Thermistor configuration
SERIES_RESISTOR = 10      # kΩ value of your fixed resistor
NOMINAL_RESISTANCE = 10   # kΩ thermistor resistance at 25°C
B_COEFFICIENT = 3950      # Beta coefficient of thermistor

# UTC offset in seconds — BST = 3600, GMT = 0
UTC_OFFSET = 3600

adc = ADC(26)
led = Pin("LED", Pin.OUT)


def connect_wifi():
    """
    Connect to WiFi using provided SSID and PASSWORD.

    Returns:
        wlan (network.WLAN): Connected WLAN object

    Raises:
        RuntimeError: If connection fails within the timeout period

    Notes:
        - LED is ON while connecting
        - LED blinks rapidly if connection fails
        - Timeout duration can be adjusted in the loop below
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    led.on()

    for _ in range(20):  # Seconds to wait (adjustable)
        if wlan.isconnected():
            led.off()
            return wlan
        time.sleep(1)

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
        - Syncs to UTC via ntptime
        - UTC_OFFSET is applied separately in get_timestamp()
        - WiFi is disabled after sync to reduce power draw
    """
    ntptime.settime()
    wlan.disconnect()
    wlan.active(False)


def read_temp():
    """
    Read temperature from thermistor using ADC and convert to Celsius.

    Returns:
        float: Temperature in degrees Celsius
        None: If voltage reading is invalid (e.g. divide-by-zero risk)

    Notes:
        - Uses Beta equation approximation
        - Adjust SERIES_RESISTOR, NOMINAL_RESISTANCE, B_COEFFICIENT as needed
    """
    adc_value = adc.read_u16()
    voltage = adc_value / 65535.0 * 3.3

    if voltage >= 3.3:
        return None

    Rt = SERIES_RESISTOR * voltage / (3.3 - voltage)
    tempK = 1 / (
        1 / (273.15 + 25) +
        math.log(Rt / NOMINAL_RESISTANCE) / B_COEFFICIENT
    )
    return tempK - 273.15


def get_timestamp():
    """
    Generate a formatted timestamp adjusted for local timezone.

    Returns:
        str: Timestamp in format 'YYYY-MM-DD HH:MM:SS'

    Notes:
        - Based on UTC time synced via NTP
        - Adjust UTC_OFFSET at the top of the file for your timezone
    """
    t = time.localtime(time.time() + UTC_OFFSET)
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )


def init_log_file():
    """
    Create CSV log file if it does not already exist.

    Notes:
        - Adds header row on first creation
        - Safe to call on every boot
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
        - File grows indefinitely — consider periodic transfer for long runs
    """
    timestamp = get_timestamp()
    with open("temps.csv", "a") as f:
        f.write("{},{:.2f}\n".format(timestamp, temp))
    print(timestamp, temp)


wlan = connect_wifi()

for _ in range(3):
    led.toggle()
    time.sleep(0.5)
led.off()

sync_time(wlan)
init_log_file()

# Main loop
while True:
    temp = read_temp()
    if temp is not None:
        log_temperature(temp)

    # Brief LED blink to confirm a logging event — remove if power is a concern
    led.toggle()
    time.sleep(1)
    led.toggle()

    time.sleep(59)  # Seconds between readings
