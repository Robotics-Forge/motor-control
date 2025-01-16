# NOTE
# This works on Ubuntu

from gpiozero import Servo
from time import sleep

# GPIO pin 18
servo = Servo(18)

while True:
    servo.min()  # Move the servo to minimum position
    sleep(1)
    servo.max()  # Move the servo to maximum position
    sleep(1)
