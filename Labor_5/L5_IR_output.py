"""-----------------------------------------------------
¦    File name: L5_IR_ouput.py                          ¦
¦    Version: 1.1                                       ¦
¦    Authors:                                           ¦
¦       Jonas Josi                                      ¦
¦       Matthias Lang                                   ¦
¦       Christian Hohmann                               ¦
¦       Joschka Maters                                  ¦
¦    Date created: 2024/05/15                           ¦
¦    Last modified: 2024/10/06                          ¦
¦    Python Version: 3.11.2                             ¦
------------------------------------------------------"""

# ----------- import external Python module -----------
from grove.adc import ADC
import time


# ----------- global constant -----------
IR_SENSOR = 2  # Connect the Grove 80cm Infrared Proximity Sensor to analog port A2

N_MEASUREMENTS = 200  # number of measurements (of ir sensor) to make, before calculating the average value
MESUREMENT_INTERVAL = 0.5  # interval time in [s] between two measurements

ADC_REF = 3.3  # Reference voltage of ADC (which is built-in the GrovePi-Board) is 5 V
ADC_RES = 4095  # The ADC on the GrovePi-Board has a resolution of 10 bit -> 1024 different digital levels in range of 0-1023

adc = ADC() # Create ADC Object once


# ----------- function definition -----------
def read_voltage_ir_sensor(port):
    """
    Returns the current voltage in [V] of the infrared proximity sensor by mapping the (digital) value returned
    by the function grovepi.analogRead() to the reference voltage of the ADC (analog-to-digital-converter)

    Parameters
    ----------
    port : int
        analog port of GrovePi connected to infrared proximity sensor.

    Returns
    -------
    float or False
        if measurment of proximity sensor doesn't fail, the voltage on pin of infrared proximity sensor in [V]
        is returned. Otherwise False is returned.
    """
    try:
        sensor_value = adc.read(port)  # digital value between 0 and 1023 (see constant "ADC_RES")
    except IOError:
        print(f"Error to read analog port {port}: {IOError}")
        return False
    voltage = float(sensor_value) * ADC_REF / ADC_RES
    return voltage


# ----------- main code -----------
if __name__ == "__main__":

    while True:
        try:
            measurement = 0
            sum_voltage = 0

            while measurement < N_MEASUREMENTS:
                voltage = read_voltage_ir_sensor(IR_SENSOR)
                if voltage:
                    sum_voltage += voltage
                    measurement += 1

            # calculate average voltage of all measurements done
            average_voltage = sum_voltage / N_MEASUREMENTS

            # Calculate distance using sensor characteristics, coefficients found from calibration (L5_IR_kalibrieren.py)
            distance = round(44.593 * average_voltage * average_voltage - 152.73 * average_voltage + 159.38, 2)

            # Print output and pause
            print(f"voltage: {round(average_voltage,2)} [V] -> distance: {distance} [mm]")
            time.sleep(MESUREMENT_INTERVAL)

        except KeyboardInterrupt:
            print("Script stopped")
            exit(0)
