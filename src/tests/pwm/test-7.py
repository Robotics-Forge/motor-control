from gpiozero import PWMOutputDevice
from time import sleep

# GPIO Pin Configuration
SERVO_PIN = 18  # Connect the control signal wire (orange) to GPIO18

# Set up the PWM device with a 50Hz frequency
pwm = PWMOutputDevice(SERVO_PIN, frequency=50)  # 50Hz = 20ms period

# Adjust these values if necessary
FULL_REVERSE_PULSE = 1.0  # Full reverse pulse width in ms
NEUTRAL_PULSE = 1.5       # Neutral (stop) pulse width in ms
FULL_FORWARD_PULSE = 2.0  # Full forward pulse width in ms

def set_fs90r_speed(speed):
    """
    Sets the speed and direction of the FS90R servo.
    :param speed: Speed range from -1.0 to 1.0
                  -1.0 = Full reverse
                   0.0 = Stop
                   1.0 = Full forward
    """
    if -1.0 <= speed <= 1.0:
        # Map speed to pulse width
        pulse_width_ms = NEUTRAL_PULSE + (speed * (FULL_FORWARD_PULSE - NEUTRAL_PULSE))
        duty_cycle = pulse_width_ms / 20  # Convert pulse width to duty cycle
        pwm.value = duty_cycle
        print(f"Speed: {speed}, Pulse Width: {pulse_width_ms:.3f} ms, Duty Cycle: {duty_cycle:.3f}")
    else:
        print("Speed must be between -1.0 and 1.0.")

    sleep(2)

try:
    while True:
        print("Controlling FS90R Servo:")
        print("1. Full forward")
        print("2. Half forward")
        print("3. Stop")
        print("4. Half reverse")
        print("5. Full reverse")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            set_fs90r_speed(1.0)  # Full forward
        elif choice == "2":
            set_fs90r_speed(0.5)  # Half forward
        elif choice == "3":
            set_fs90r_speed(0.0)  # Stop
        elif choice == "4":
            set_fs90r_speed(-0.5)  # Half reverse
        elif choice == "5":
            set_fs90r_speed(-1.0)  # Full reverse
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

finally:
    pwm.off()
    print("Exiting.")
