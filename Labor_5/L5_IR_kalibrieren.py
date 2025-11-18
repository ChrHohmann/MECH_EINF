"""-----------------------------------------------------
¦    File name: L5_IR_kalibrieren.py                    ¦
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
import csv


# ----------- global constant -----------
CSV_FILENAME = "Sensorkalibrierung.csv"  # *** CHANGE ME *** file to save calibration data for infrared sensor
CSV_DELIMITER = ";"  # *** CHANGE ME *** Character to separate data fields / cells in the CSV file

IR_SENSOR = 2  # Connect the Grove 80cm Infrared Proximity Sensor to analog port A2

MIN_MEAS_DIST = 25  # minimum measurement distance in [mm]
MAX_MEAS_DIST = 65  # max measurement distance in [mm]
INCREMENT_MEAS_DIST = 5  # increment in [mm] of two consecutive measurement distances
N_MEASUREMENTS = 200  # number of measurements (of ir sensor) to be done for each measurement distance
N_MEASUREMENTS_CYCLES = 1  # number of measurements cycles (towards, away) from sensor

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

def create_csv_file(filename):
    """
    If not already existing, create csv-file.

    Parameters
    ----------
    filename : String
        Path of csv-file to be created. The path can be either absolute (full path) or a relative path to the path of
        this script.

    Returns
    -------
    bool
        True if the file was successfully created.
        False if the file could not be created.
    """
    try:
        # if csv-file not already exists, try to create the file
        with open(filename, 'x') as csvfile:
            pass  # do nothing
        return True
    except FileExistsError:
        print(f"csv-file '{filename}' cannot be created since it already exists")
        return False


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


# ----------- main code -----------

if __name__ == "__main__":
    
    # create csv-file
    if not create_csv_file(CSV_FILENAME):
        exit(1)  # csv-file cannot be created or already exists -> stop script

    # add first row (with table headers) to csv file
    add_row_to_csv(CSV_FILENAME, f"Spannung (V){CSV_DELIMITER} Abstand (mm){CSV_DELIMITER}", CSV_DELIMITER)

    try:
        for _ in range(N_MEASUREMENTS_CYCLES):
            meas_dist = MAX_MEAS_DIST
            while meas_dist >= MIN_MEAS_DIST:
                input(f"Fahre auf {meas_dist} mm (Mit Enter bestaetigen)")

                measurement = 0
                sum_voltage = 0

                while measurement < N_MEASUREMENTS:
                    voltage = read_voltage_ir_sensor(IR_SENSOR)
                    if voltage:
                        sum_voltage += voltage
                        measurement += 1

                average_voltage = sum_voltage / N_MEASUREMENTS
                print(f"dist: {meas_dist} [mm] -> voltage: {average_voltage} [V]")
                print("-" * 50)

                # append row to csv file with measurement data
                add_row_to_csv(CSV_FILENAME, f"{average_voltage}{CSV_DELIMITER}{meas_dist}", CSV_DELIMITER)

                meas_dist -= INCREMENT_MEAS_DIST

            meas_dist = MIN_MEAS_DIST
            while meas_dist <= MAX_MEAS_DIST:
                input(f"Fahre auf {meas_dist} mm (Mit Enter bestaetigen)")

                measurement = 0
                sum_voltage = 0

                while measurement < N_MEASUREMENTS:
                    voltage = read_voltage_ir_sensor(IR_SENSOR)
                    if voltage:
                        sum_voltage += voltage
                        measurement += 1

                average_voltage = sum_voltage / N_MEASUREMENTS
                print(f"dist: {meas_dist} [mm] -> voltage: {average_voltage} [V]")
                print("-" * 50)

                # append row to csv file with measurement data
                add_row_to_csv(CSV_FILENAME, f"{average_voltage}{CSV_DELIMITER}{meas_dist}", CSV_DELIMITER)

                meas_dist += INCREMENT_MEAS_DIST

    except KeyboardInterrupt:
        print("Script stopped")
        pass

    print("\n" + f"*** Calibration-Measurements successfully finished. Data is saved to file '{CSV_FILENAME}' ***")
