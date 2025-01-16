from gpiozero import Servo
from time import sleep

# GPIO Pin Configuration - Left Hand
LEFT_THUMB_PIN = 18
LEFT_THUMB_ROTATE_PIN = 24
LEFT_INDEX_PIN = 17
LEFT_MIDDLE_PIN = 27
LEFT_RING_PIN = 22
LEFT_PINKY_PIN = 23

# GPIO Pin Configuration - Right Hand
RIGHT_THUMB_PIN = 5
RIGHT_THUMB_ROTATE_PIN = 6
RIGHT_INDEX_PIN = 13
RIGHT_MIDDLE_PIN = 19
RIGHT_RING_PIN = 26
RIGHT_PINKY_PIN = 16

# Create servo instances - Left Hand
left_thumb = Servo(LEFT_THUMB_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
left_thumb_rotate = Servo(LEFT_THUMB_ROTATE_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
left_index = Servo(LEFT_INDEX_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
left_middle = Servo(LEFT_MIDDLE_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
left_ring = Servo(LEFT_RING_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
left_pinky = Servo(LEFT_PINKY_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

# Create servo instances - Right Hand
right_thumb = Servo(RIGHT_THUMB_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_thumb_rotate = Servo(RIGHT_THUMB_ROTATE_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_index = Servo(RIGHT_INDEX_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_middle = Servo(RIGHT_MIDDLE_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_ring = Servo(RIGHT_RING_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
right_pinky = Servo(RIGHT_PINKY_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

# Group servos by hand
left_hand_servos = [left_thumb, left_index, left_middle, left_ring, left_pinky]
right_hand_servos = [right_thumb, right_index, right_middle, right_ring, right_pinky]

def control_hand(hand, angle):
    """
    Controls the specified hand's position.
    :param hand: String 'left' or 'right' to specify which hand to control
    :param angle: Value between -1 (closed) and 1 (open)
    """
    try:
        servos = left_hand_servos if hand.lower() == 'left' else right_hand_servos
        for servo in servos:
            servo.value = angle
        print(f"Setting {hand} hand to position: {angle}")
        sleep(0.5)  # Give servos time to reach position
    except Exception as e:
        print(f"Error setting positions: {e}")

# Example usage:
# try:
#     while True:
#         hand = input("Enter hand to control (left/right) or 'exit' to quit: ").lower()
#         if hand == 'exit':
#             break
#         if hand not in ['left', 'right']:
#             print("Invalid hand. Please enter 'left' or 'right'")
#             continue

#         angle = input("Enter angle (-1 to 1): ")
#         try:
#             angle = float(angle)
#             if -1 <= angle <= 1:
#                 control_hand(hand, angle)
#             else:
#                 print("Angle must be between -1 and 1")
#         except ValueError:
#             print("Invalid angle. Please enter a number between -1 and 1")

# finally:
#     # Cleanup - detach all servos
#     for servo in left_hand_servos + right_hand_servos:
#         servo.detach()
#     print("Exiting.")
