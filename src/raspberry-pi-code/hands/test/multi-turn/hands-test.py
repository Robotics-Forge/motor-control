from gpiozero import PWMOutputDevice
from time import sleep

# GPIO Pin Configuration
SERVO_PIN_1 = 18  # First hand
SERVO_PIN_2 = 17  # Second hand

# Set up two PWM devices
pwm1 = PWMOutputDevice(SERVO_PIN_1, frequency=50)
pwm2 = PWMOutputDevice(SERVO_PIN_2, frequency=50)

# Adjust these values if necessary
FULL_REVERSE_PULSE = 1.5 # Full reverse pulse width in ms
NEUTRAL_PULSE = 1.6     # Neutral (stop) pulse width in ms
FULL_FORWARD_PULSE = 1.7  # Full forward pulse width in ms

def set_fs90r_speed(speed, hand_num, duration=1.0):
    """
    Sets the speed and direction of the specified hand's FS90R servo.
    :param speed: Speed range from -1.0 to 1.0
    :param hand_num: Hand number (1 or 2)
    :param duration: How long to run the servo (default 1 second)
    """
    if -1.0 <= speed <= 1.0:
        # New calculation using all three pulse values
        pulse_width_ms = NEUTRAL_PULSE
        if speed >= 0:
            pulse_width_ms = NEUTRAL_PULSE + (speed * (FULL_FORWARD_PULSE - NEUTRAL_PULSE))
        else:
            pulse_width_ms = NEUTRAL_PULSE + (speed * (NEUTRAL_PULSE - FULL_REVERSE_PULSE))

        print(pulse_width_ms)
        duty_cycle = pulse_width_ms / 20
        if hand_num == 1:
            pwm1.value = duty_cycle
        else:
            pwm2.value = duty_cycle
        print(f"Hand {hand_num} - Speed: {speed}, Duration: {duration}s")
        sleep(duration)

        # Modified stopping behavior
        if hand_num == 1:
            pwm1.value = 0  # Completely turn off the PWM signal
        else:
            pwm2.value = 0  # Completely turn off the PWM signal
    else:
        print("Speed must be between -1.0 and 1.0.")

try:
    while True:
        print("\nHand Control Options:")
        print("1. First hand - Full Close (Forward)")
        print("2. First hand - Full Open (Reverse)")
        print("3. Second hand - Full Close (Forward)")
        print("4. Second hand - Full Open (Reverse)")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "5":
            break
        elif choice == "1":
            set_fs90r_speed(1.0, 1, 1.0)    # Hand 1 full forward
        elif choice == "2":
            set_fs90r_speed(-1.0, 1, 1.0)   # Hand 1 full reverse
        elif choice == "3":
            set_fs90r_speed(1.0, 2, 1.0)    # Hand 2 full forward
        elif choice == "4":
            set_fs90r_speed(-1.0, 2, 1.0)   # Hand 2 full reverse
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

finally:
    pwm1.off()
    pwm2.off()
    print("Exiting.")
