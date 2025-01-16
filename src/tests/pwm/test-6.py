from gpiozero import Servo
from time import sleep

# GPIO Pin Configuration
SERVO_PIN = 18  # Connect the control signal wire (orange) to GPIO18

# Fine-tune pulse width range for FS90R
# Default values might not stop the servo precisely, so adjustments are made
servo = Servo(SERVO_PIN, min_pulse_width=0.001, max_pulse_width=0.002)

# Function to set the speed and direction of the FS90R servo
def set_fs90r_speed(speed):
    """
    Sets the speed and direction of the FS90R servo.
    :param speed: Speed range from -1.0 to 1.0
                  -1.0 = Full reverse
                   0.0 = Stop
                   1.0 = Full forward
    """
    if -1.0 <= speed <= 1.0:
        servo.value = speed
    else:
        print("Speed must be between -1.0 and 1.0.")

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

        sleep(2)  # Wait to observe the movement

finally:
    # Cleanup (gpiozero handles GPIO cleanup automatically on program exit)
    servo.detach()
    print("Exiting.")
