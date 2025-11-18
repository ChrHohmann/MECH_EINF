"""-----------------------------------------------------
¦    File name: L5_Regelkreis_drehzahl.py               ¦
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
import lgpio
import os
import re
import csv
import time


# ----------- global constant -----------
""" Settings """
k = 2                  # *** CHANGE ME *** controller amplification factor k [mm^-1]
N_MEASUREMENTS = 10    # *** CHANGE ME *** number of distance measurements [] over which to average
DRIVETIME = 0.1        # *** CHANGE ME *** time in [s] to drive the motor with a specific voltage before recalculate the voltage
OFFSET_DUTYCYCLE = 10  # *** CHANGE ME *** value [dmnl] to add to calculated duty_cycle of controller. This prevents that the motor is driven by a voltage which is to small to rotate the motor shaft.

# results-file parameters
CSV_FILENAME = "Wegdiagramm_Drehzahl.csv"  # *** CHANGE ME *** file to log data (timestamp and distance)
CSV_DELIMITER = ";"  # *** CHANGE ME *** Character to separate data fields / cells in the CSV file

# assign Grove BaseHat Ports
IR_SENSOR = 2  # Connect the Grove 80cm Infrared Proximity Sensor to analog port A2

# assign motor driver interface to GPIO's of Raspberry Pi
M3 = 6        # M3 on Motor screw terminal
M4 = 13       # M4 on Motor screw terminal 
PWMB = 12     # GPIO to be pulsed

# analog-digital-converter parameters
adc = ADC()
ADC_REF = 3.3  # Reference voltage of ADC (which is built-in the GrovePi-Board) is 5 V
ADC_RES = 4095  # The ADC on the GrovePi-Board has a resolution of 10 bit -> 1024 different digital levels in range of 0-1023

# auxiliary parameters
MAX_VOLTAGE = 12  # supply voltage of motor driver is 12 V (which equals the max. rated voltage of the DC motor)
PWM_FREQUENCY = 1000  # Hz


# ----------- function definition -----------
def stop_motor():
    """
    Set state of both output pins of the motor driver (M1, M2) to LOW (0 V).
    Then disable the motor driver output pins (M1, M2).
    """
    # set state of motor driver outputs (M1 and M2) to low (0 V)
    lgpio.gpio_write(gpio0, M3, 0)
    lgpio.gpio_write(gpio0, M4, 0)

    # disable motor driver by setting PWM duty cycle to 0%
    lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, 0)

    print("\nMotor stopped")


def create_csv_file(filename):
    """
    If the CSV file does not exist, create it. If the filename already exists, append an underscore followed by the next
    available integer to the filename.

    Parameters
    ----------
    filename : str
        Path of the CSV file to be created. The path can be either absolute (full path) or a relative path to the directory of
        this script.

    Returns
    -------
    str or None
        If the CSV file was successfully created the filename is returned.
        If creating the CSV file failed, None is returned.
    """
    try:
        if os.path.exists(filename):  # Check if filename already exists
            # Remove the ".csv" suffix if file ends with ".csv"
            if filename.endswith(".csv"):
                filename = filename[:-4]
            pattern = re.compile(rf'{re.escape(filename)}_(\d+)\.csv$')  # Pattern to match underscore followed by numbers at end of filename
            matches = [pattern.search(f) for f in os.listdir('.') if pattern.search(f) and f.startswith(filename)]
            existing_suffixes = [int(match.group(1)) for match in matches]
            next_suffix = max(existing_suffixes, default=0) + 1
            filename = f"{filename}_{next_suffix}.csv"  # Update filename with next available suffix
        with open(filename, 'x') as csvfile:
            return filename
    except Exception as e:
        print(f"Error creating CSV file '{filename}': {e}")
        return None


def add_row_to_csv(filename, row_data, delimiter):
    """
    Add a row of data to an existing csv-file.

    Parameters
    ----------
    filename : String
        Path of csv-file to be append by an row. The path can be either absolute (full path) or a relative path
        to the path of this script.
    row_data : String
        Data to be added to the new row.
    delimiter : String
        Character or string used to separate data fields in the CSV file.


    Returns
    -------
    bool
        True if a row with data was successfully added to the csv-file.
        False if adding a row with data to the csv-file failed.
    """
    try:
        # open csv-file in append mode ('a')
        with open(filename, 'a') as csvfile:
            # create csv_writer object
            csv_writer = csv.writer(csvfile, delimiter=delimiter)

            # convert string into a list in which each entry has the value of a cell
            lst_cell_values = row_data.split(delimiter)

            # append row to csv file (with corresponding data)
            csv_writer.writerow(lst_cell_values)
        return True
    except Exception as e:
        print(f"Error to add row '{row_data}' to csv-file '{filename}': {e}")
        return False

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
    # initialize lgpio
    gpio0 = lgpio.gpiochip_open(0)  # Open GPIO chip 0

    # Configure GPIO pins as outputs
    lgpio.gpio_claim_output(gpio0, M3)
    lgpio.gpio_claim_output(gpio0, M4) 
    lgpio.gpio_claim_output(gpio0, PWMB)
    
    # Initialize all pins to safe state
    lgpio.gpio_write(gpio0, M3, 0)
    lgpio.gpio_write(gpio0, M4, 0)
    lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, 0)  # PWM at 0% initially

    # Ask user for the Set-distance
    valid_userinput = False
    while not valid_userinput:
        userinput = input("Auf welche Distanz zwischen 30 mm und 60 mm soll gefahren werden? ")
        if userinput.isdigit():  # if userinput includes only digits
            if 30 <= int(userinput) <= 60:  # check if userinput is within range 30 - 60 mm
                valid_userinput = True
            else:
                print("nur Werte zwischen 30 und 60 als Input erlaubt")
        else:
            print("nur ganze Zahlen als Input erlaubt")

    set_distance = float(userinput)
    filename = create_csv_file(CSV_FILENAME)
    if filename:
        print(f"csv-file '{filename}' created")
    else:
        print(f"failed to create csv-file '{CSV_FILENAME}'")
        exit(0)

    # add first row to csv file, with parameters this script
    if CSV_DELIMITER == ",":
        add_row_to_csv(filename,
                       f"k={k} (mm^-1); drivetime={DRIVETIME} (s); nmeasurements={N_MEASUREMENTS}; offset_dutycycle={OFFSET_DUTYCYCLE}; set_distance={int(set_distance)} (mm)",
                       CSV_DELIMITER)
    elif CSV_DELIMITER == ";":
        add_row_to_csv(filename,
                       f"k={k} (mm^-1), drivetime={DRIVETIME} (s), nmeasurements={N_MEASUREMENTS}, offset_dutycycle={OFFSET_DUTYCYCLE}, set_distance={int(set_distance)} (mm)",
                       CSV_DELIMITER)
    else:
        add_row_to_csv(filename,
                       f"k={k} (mm^-1)  drivetime={DRIVETIME} (s)  nmeasurements={N_MEASUREMENTS}  offset_dutycycle={OFFSET_DUTYCYCLE}  set_distance={int(set_distance)} (mm)",
                       CSV_DELIMITER)

    # add second row to csv file, with table headers
    add_row_to_csv(filename, f"time (s){CSV_DELIMITER}ist_distanz (mm){CSV_DELIMITER}delta_distance (mm)", CSV_DELIMITER)

    start_timestamp = None

    """ control loop with constant drivetime and dynamically calculated speed/dutycycle """
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
            distance = round(634.24 * average_voltage * average_voltage - 545.7 * average_voltage + 142.5, 2)

            if start_timestamp:
                time_elapsed = round(time.time() - start_timestamp, 3)
            else:
                start_timestamp = time.time()
                time_elapsed = 0

            # Compare current distance with set distance
            delta_distance = set_distance - distance  # control error

            # update csv-file
            add_row_to_csv(filename, f"{time_elapsed}{CSV_DELIMITER}{distance}{CSV_DELIMITER}{round(delta_distance, 3)}", CSV_DELIMITER)

            # calculate speed to drive the motor
            speed = delta_distance * k
            pwm_dutycycle = int(round(abs(speed) + OFFSET_DUTYCYCLE, 0))
            print(pwm_dutycycle)

            # make sure that the pwm dutycycle is within range 0-255 (8 Bit)
            if pwm_dutycycle < 0:
                pwm_dutycycle = 0
            if pwm_dutycycle > 100:
                pwm_dutycycle = 100

            print(f"ist: {distance} mm, soll: {set_distance} mm -> delta_dist: {round(delta_distance, 4)} mm -> speed: {round(speed, 4)}")

            # define motor direction
            if speed >= 0:
                direction = 0
            else:
                direction = 1

            # drive motor with calculated speed/voltage for constant drivetime
            if direction == 0:
                 # set direction: M3 HIGH, M4 LOW
                lgpio.gpio_write(gpio0, M3, 1)
                lgpio.gpio_write(gpio0, M4, 0)
                # set PWM signal 
                lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, pwm_dutycycle)
            elif direction == 1:
                 # set direction: M3 HIGH, M4 LOW
                lgpio.gpio_write(gpio0, M3, 0)
                lgpio.gpio_write(gpio0, M4, 1)
                # set PWM signal 
                lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, pwm_dutycycle)
            time.sleep(DRIVETIME)
        except KeyboardInterrupt:
            stop_motor()
            # Free GPIO pins
            lgpio.gpio_free(gpio0, M3)
            lgpio.gpio_free(gpio0, M4)
            lgpio.gpio_free(gpio0, PWMB)
            lgpio.gpiochip_close(gpio0)  # Close the GPIO chip connection
            print("\n " + "*" * 5 + f" Measurement stopped. Data saved to Log-File: {filename} " + "*" * 5 + "\n ")
            print("Exit Python")
            exit(0)  # exit python with exit code 0
