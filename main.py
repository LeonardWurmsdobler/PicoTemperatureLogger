import machine
from machine import Pin, ADC
import time
import math

# No WiFi in this version — timestamps are relative to boot time

SERIES_RESISTOR = 10         # kΩ value of your fixed resistor
NOMINAL_RESISTANCE = 10      # kΩ thermistor resistance at 25°C
B_COEFFICIENT = 3950         # Beta coefficient of thermistor


adc = ADC(26) # GPIO pin used for thermistor (ADC0 = GP26)
led = Pin("LED", Pin.OUT) # Onboard LED is "LED", can be changed to an external LED


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
        - Adjust constants for better accuracy
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
    Generate a timestamp based on system uptime.

    Returns:
        str: Timestamp in format 'seconds_since_boot'

    Notes:
        - No real-world time without WiFi/NTP
        - Useful for relative timing between readings
    """
    return str(time.time())


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


init_log_file()

#Main Loop
while True:
    temp = read_temp()

    if temp is not None:
        log_temperature(temp)

    # LED blink to indicate logging event, can be removed
    led.toggle()
    time.sleep(1)
    led.toggle()

    time.sleep(59) # Time between temperature readings (seconds)
