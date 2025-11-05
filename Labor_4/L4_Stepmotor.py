"""-----------------------------------------------------
¦    File name: L4_DCmotor.py                           ¦
¦    Version: 1.1                                       ¦
¦    Authors:                                           ¦
¦       Jonas Josi                                      ¦
¦       Matthias Lang                                   ¦
¦       Christian Hohmann                               ¦
¦       Joschka Maters                                  ¦
¦    Date created: 2024/05/01                           ¦
¦    Last modified: 2025/10/06                          ¦
¦    Python Version: 3.11.2                             ¦
------------------------------------------------------"""

# ----------- import external Python module -----------
import lgpio
import time


# ----------- global constant -----------
# assign motor driver interface to GPIO's of Raspberry Pi
M1 = 20  # M1 on Motor screw terminal - connetct to signal A on coil 1
M2 = 21  # M2 on Motor screw terminal - connetct to signal A/ on coil 1
M3 = 6   # M3 on Motor screw terminal - connetct to signal B on coil 2
M4 = 13  # M4 on Motor screw terminal - connetct to signal B/ on coil 2
D1 = 26  # enable/disable output pins M1, M2
D2 = 12  # enable/disable output pins M3, M4

# settings of stepper motor
DIRECTION = 0  # *** CHANGE ME *** movement direction (0 or 1) of slide on linear guideway
STEP_TIME = 0.003  # *** CHANGE ME *** time in [s] between two consecutive steps of stepper motor


# ----------- function definition -----------
def set_motor_coils(coil_1, coil_2, coil_3, coil_4):
    """
    Set state (HIGH/LOW) of all 4 coils of stepper motor by controlling the output pins of the motor driver (M1, M2, M3, M4).

    Parameters
    ----------
    coil_1 : int or GPIO.LOW or GPIO.HIGH
    coil_2 : int or GPIO.LOW or GPIO.HIGH
    coil_3 : int or GPIO.LOW or GPIO.HIGH
    coil_4 : int or GPIO.LOW or GPIO.HIGH
    """
    lgpio.gpio_write(gpio0, M1, coil_1)
    lgpio.gpio_write(gpio0, M2, coil_2)
    lgpio.gpio_write(gpio0, M3, coil_3)
    lgpio.gpio_write(gpio0, M4, coil_4)


def busy_sleep(secs):
    """
    Actively waits for a specified time by keeping the CPU busy in a loop. This has the advantage over a passive sleep
    (i.e. time.sleep()) that a more precise timing / sleep time can be achieved. However, it may consume more
    CPU resources compared to a passive sleep method.

    Parameters
    ----------
    secs : float
        The wait time in seconds. Can be a decimal number.
    """
    start_timestamp = time.time()
    # if sleep time is more than 4 ms, make a passive sleep of sleep time - 2 ms to reduce cpu resources
    if secs > 0.0004:
        time.sleep(secs - 0.0002)
    while time.time() - start_timestamp < secs:
        pass  # do nothing


def stop_motor():
    """
    Set state of all 4 coils of stepper motor to LOW by controlling the output pins of the motor driver (M1, M2, M3, M4).
    Then disable all motor driver output pins (M1, M2, M3, M4).
    """
    # enable motor driver outputs
    lgpio.gpio_write(gpio0, D1, 1)  # enable output pins M1, M2
    lgpio.gpio_write(gpio0, D2, 1)  # enable output pins M3, M4

    # turn off all coils
    set_motor_coils(0, 0, 0, 0)
    busy_sleep(STEP_TIME)

    # disable motor driver outputs
    lgpio.gpio_write(gpio0, D1, 0)  # disable output pins M1, M2
    lgpio.gpio_write(gpio0, D2, 0)  # disable output pins M3, M4
    print("\nMotor stopped")


# ----------- main code -----------
if __name__ == "__main__":
    # initialize lgpio
    gpio0 = lgpio.gpiochip_open(0) # open GPIO chip 0

    # initialize all pins to safe state 
    lgpio.gpio_write(gpio0, M1, 0)
    lgpio.gpio_write(gpio0, M2, 0)
    lgpio.gpio_write(gpio0, M3, 0)
    lgpio.gpio_write(gpio0, M4, 0)
    lgpio.gpio_write(gpio0, D1, 0)
    lgpio.gpio_write(gpio0, D2, 0)

    # enable motor driver outputs
    lgpio.gpio_write(gpio0, D1, 1)  # enable output pins M1, M2
    lgpio.gpio_write(gpio0, D2, 1)  # enable output pins M3, M4

    try:
        # endless loop
        while True:
            if DIRECTION == 0:
                # activate coil 2 & coil 4
                set_motor_coils(0, 1, 0, 1)
                busy_sleep(STEP_TIME)
                # activate coil 2 & coil 3
                set_motor_coils(0, 1, 1, 0)
                busy_sleep(STEP_TIME)
                # activate coil 1 & coil 3
                set_motor_coils(1, 0, 1, 0)
                busy_sleep(STEP_TIME)
                # activate coil 1 & coil 4
                set_motor_coils(1, 0, 0, 1)
                busy_sleep(STEP_TIME)
            else:
                # activate coil 1 & coil 4
                set_motor_coils(1, 0, 0, 1)
                busy_sleep(STEP_TIME)
                # activate coil 1 & coil 3
                set_motor_coils(1, 0, 1, 0)
                busy_sleep(STEP_TIME)
                # activate coil 2 & coil 3
                set_motor_coils(0, 1, 1, 0)
                busy_sleep(STEP_TIME)
                # activate coil 2 & coil 4
                set_motor_coils(0, 1, 0, 1)
                busy_sleep(STEP_TIME)

    # detect exception - usually triggered by a user input, stopping the script
    except KeyboardInterrupt:
        stop_motor()
        # Free GPIO pins
        lgpio.gpio_free(gpio0, M1)
        lgpio.gpio_free(gpio0, M2)
        lgpio.gpio_free(gpio0, M3)
        lgpio.gpio_free(gpio0, M4)
        lgpio.gpiochip_close(gpio0) # Close the GPIO chip connection
        print("Exit Python")
        exit(0)  # exit python with exit code 0