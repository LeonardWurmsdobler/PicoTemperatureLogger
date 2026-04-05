from machine import Pin, ADC
import time
import math

# No WiFi in this version — timestamps are seconds elapsed since boot

# Thermistor configuration
SERIES_RESISTOR = 10      # kΩ value of your fixed resistor
NOMINAL_RESISTANCE = 10   # kΩ thermistor resistance at 25°C
B_COEFFICIENT = 3950      # Beta coefficient of thermistor

adc = ADC(26)
led = Pin("LED", Pin.OUT)


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
    Return seconds elapsed since boot as a timestamp.

    Returns:
        str: Seconds since boot

    Notes:
        - No real-world clock without WiFi/NTP
        - Use the wireless version for wall-clock timestamps
    """
    return str(time.time())


def init_log_file():
    """
    Create CSV log file if it does not already exist.

    Notes:
        - Adds header row on first creation
        - Safe to call on every boot
    """
    try:
        with open("temps.csv", "x") as f:
            f.write("seconds_since_boot,temperature\n")  # reflects actual column content
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
