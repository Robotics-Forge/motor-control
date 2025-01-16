import pigpio
import time

# GPIO pin
SERVO_PIN = 18

# Initialize pigpio library
pi = pigpio.pi()

if not pi.connected:
    exit()

# Function to move the servo to a specific angle (0 to 270)
def move_servo(angle):
    # Map the angle (0-270) to the corresponding PWM pulse (500-2500)
    pulse_width = int(500 + (angle / 270) * 2000)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

try:
    while True:
        # Move to 0 degrees (500 us pulse)
        move_servo(0)
        print("Servo at 0 degrees")
        time.sleep(2)

        # Move to 90 degrees (1500 us pulse)
        move_servo(90)
        print("Servo at 90 degrees")
        time.sleep(2)

        # Move to 180 degrees (2000 us pulse)
        move_servo(180)
        print("Servo at 180 degrees")
        time.sleep(2)

        # Move to 270 degrees (2500 us pulse)
        move_servo(270)
        print("Servo at 270 degrees")
        time.sleep(2)

except KeyboardInterrupt:
    pass

finally:
    pi.stop()  # Cleanup
