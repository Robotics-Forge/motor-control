from gpiozero import Servo
from time import sleep

# GPIO Pin Configuration
SERVO_PIN = 18

# Create servo instance with adjusted pulse widths for SG90
# SG90 typically uses pulse widths between 0.5ms (-90 degrees) and 2.5ms (+90 degrees)
servo = Servo(SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

def set_position(angle):
    """
    Sets the position of the SG90 servo.
    :param angle: Value between -1 (closed) and 1 (open)
    """
    try:
        servo.value = angle
        print(f"Setting position to: {angle}")
        sleep(0.5)  # Give servo time to reach position
    except Exception as e:
        print(f"Error setting position: {e}")

try:
    while True:
        print("\nHand Control Options:")
        print("1. Full Open (90 degrees)")
        print("2. Full Close (-90 degrees)")
        print("3. Middle Position (0 degrees)")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "4":
            break
        elif choice == "1":
            set_position(1.0)    # Full open
        elif choice == "2":
            set_position(-1.0)   # Full close
        elif choice == "3":
            set_position(0.0)    # Middle position
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

finally:
    servo.detach()
    print("Exiting.")
