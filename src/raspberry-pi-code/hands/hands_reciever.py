from gpiozero import Servo
from time import sleep
from hands_util import control_hand

# Define input servo pins
LEFT_CONTROL_SERVO_PIN = 20   # Choose an unused GPIO pin
RIGHT_CONTROL_SERVO_PIN = 21  # Choose an unused GPIO pin

# Create input servo instances
left_control_servo = Servo(LEFT_CONTROL_SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_control_servo = Servo(RIGHT_CONTROL_SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

def monitor_control_servos():
    """
    Continuously monitors the position of control servos and mirrors their position to all fingers
    """
    try:
        while True:
            # Read positions from control servos
            left_position = left_control_servo.value
            right_position = right_control_servo.value

            # Update all servos in each hand
            control_hand('left', left_position)
            control_hand('right', right_position)

            # Small delay to prevent overwhelming the system
            sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting program")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        left_control_servo.detach()
        right_control_servo.detach()

if __name__ == "__main__":
    print("Starting hand control monitoring...")
    print("Use Ctrl+C to exit")
    monitor_control_servos()
