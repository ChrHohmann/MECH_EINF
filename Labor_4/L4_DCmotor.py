"""-----------------------------------------------------
¦    File name: L4_DCmotor.py                           ¦
¦    Version: 1.1                                       ¦
¦    Authors:                                           ¦
¦       Jonas Josi                                      ¦
¦       Matthias Lang                                   ¦
¦       Christian Hohmann                               ¦
¦    Date created: 2024/05/01                           ¦
¦    Last modified: 2025/08/27                          ¦
¦    Python Version: 3.11.2                             ¦
------------------------------------------------------"""

# ----------- import external Python module -----------
import lgpio  # library to create hardware-based PWM signals on Raspberry Pi


# ----------- global constant -----------
# assign motor driver interface to GPIO's of Raspberry Pi
M3 = 6     # M3 on Motor screw terminal
M4 = 13    # M4 on Motor screw terminal 
PWMB = 12  # GPIO to be pulsed

# settings
VOLTAGE = 6 # *** CHANGE ME *** voltage for DC motor [V] between 0 und 12 V (Voltage from power supply is always 12 V)
DIRECTION = 0  # *** CHANGE ME *** movement direction (0 or 1) of slide on linear guideway

# auxiliary parameters
MAX_VOLTAGE = 12  # supply voltage of motor driver is 12 V (which equals the max. rated voltage of the DC motor)
PWM_FREQUENCY = 1000  # Hz
PWM_DUTYCYCLE = round(VOLTAGE / MAX_VOLTAGE * 100, 3)  # PWM_DUTYCYCLE from 0 (OFF) to 100 percent (FULLY ON)


# ----------- function definition -----------
def stop_motor():
    """
    Set state of both output pins of the motor driver (M3, M4) to LOW (0 V).
    Then disable the motor driver by setting PWM duty cycle to 0%.
    """
    # set state of motor driver outputs (M1 and M2) to low (0 V)
    lgpio.gpio_write(gpio0, M3, 0)
    lgpio.gpio_write(gpio0, M4, 0)

    # disable motor driver by setting PWM duty cycle to 0%
    lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, 0)

    print("\nMotor stopped")


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

    print(f"Motor settings:")
    print(f"  Voltage: {VOLTAGE}V (max: {MAX_VOLTAGE}V)")
    print(f"  Direction: {DIRECTION}")
    print(f"  PWM Frequency: {PWM_FREQUENCY}Hz")
    print(f"  PWM Duty Cycle: {PWM_DUTYCYCLE}%")

    """ run motor """
    try:
        if DIRECTION == 0:
            # set direction: M3 HIGH, M4 LOW
            lgpio.gpio_write(gpio0, M3, 1)
            lgpio.gpio_write(gpio0, M4, 0)
            # set PWM signal on D1 (enable pin) for speed contro
            lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, PWM_DUTYCYCLE)

        elif DIRECTION == 1:
            # set direction: M3 LOW, M4 HIGH  
            lgpio.gpio_write(gpio0, M3, 0)
            lgpio.gpio_write(gpio0, M4, 1)
            # set PWM signal on PWMB
            lgpio.tx_pwm(gpio0, PWMB, PWM_FREQUENCY, PWM_DUTYCYCLE)            
  
        # Ask for any user input to stop motor / script
        userinput = input("Stop motor? (Press Enter for yes)")
        stop_motor()
        # Free GPIO pins
        lgpio.gpio_free(gpio0, M3)
        lgpio.gpio_free(gpio0, M4)
        lgpio.gpio_free(gpio0, PWMB)
        lgpio.gpiochip_close(gpio0)  # Close the GPIO chip connection
        print("Exit Python")
        exit(0)  # exit python with exit code 0        

    # detect exception - usually triggered by a user input, stopping the script
    except KeyboardInterrupt:
        stop_motor()
        # Free GPIO pins
        lgpio.gpio_free(gpio0, M3)
        lgpio.gpio_free(gpio0, M4)
        lgpio.gpio_free(gpio0, PWMB)
        lgpio.gpiochip_close(gpio0)  # Close the GPIO chip connection
        print("Exit Python")
        exit(0)  # exit python with exit code 0        
