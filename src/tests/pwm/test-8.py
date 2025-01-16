from gpiozero import PWMOutputDevice
from time import sleep

# GPIO Pin Configuration
SERVO_PIN = 18  # Connect the control signal wire (orange) to GPIO18

# Set up the PWM device with a 50Hz frequency
pwm = PWMOutputDevice(SERVO_PIN, frequency=50)  # 50Hz = 20ms period

# Adjust these values if necessary
FULL_REVERSE_PULSE = 1.0  # Full reverse pulse width in ms
NEUTRAL_PULSE = 1.5       # Neutral (stop) pulse width in ms (really between 1.6)
FULL_FORWARD_PULSE = 2.0  # Full forward pulse width in ms

# Direct pwm set
def set_fs90r_speed(pulse_width_ms):
    duty_cycle = pulse_width_ms / 20  # Convert pulse width to duty cycle
    pwm.value = duty_cycle

    print(f"ulse Width: {pulse_width_ms:.3f} ms, Duty Cycle: {duty_cycle:.3f}")

    sleep(2)

try:
    while True:
        print("Controlling FS90R Servo:")

        choice = input("Enter your choice (1.0-2.0): ")
        float_value = float(choice) 

        print(float_value)
        set_fs90r_speed(float_value)

finally:
    pwm.off()
    print("Exiting.")
