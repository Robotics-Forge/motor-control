# NOTE
# This works on Raspberry PI OS but not Ubuntu

import lgpio
import time

servo_pin = 18  # GPIO 18 (BCM numbering)

# Open the GPIO chip and set up the servo pin for output
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, servo_pin)

# Function to set the PWM duty cycle
def set_servo_angle(angle):
    pulse_width = 1000 + (angle / 180.0) * 1000  # Convert angle to pulse width
    duty_cycle = (pulse_width / 20000) * 100     # Convert to percentage
    lgpio.tx_pwm(h, servo_pin, 50, duty_cycle)   # 50 Hz frequency

try:
    while True:
        print("Working")
        set_servo_angle(0)    # Move to 0 degrees
        time.sleep(1)
        set_servo_angle(90)   # Move to 90 degrees
        time.sleep(1)
        set_servo_angle(180)  # Move to 180 degrees
        time.sleep(1)
except KeyboardInterrupt:
    pass

# Clean up
lgpio.gpiochip_close(h)
