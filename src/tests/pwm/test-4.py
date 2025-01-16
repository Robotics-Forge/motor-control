from gpiozero import PWMOutputDevice
from time import sleep

# GPIO pin for PWM (e.g., GPIO 18)
servo_pin = PWMOutputDevice(18, frequency=50)  # 50 Hz PWM for servo

# Function to set servo position (in degrees)
def set_servo_position(degrees):
    # Convert degrees (0-270) to duty cycle (1ms to 4ms)
    # 0 degrees corresponds to 1 ms (duty cycle 0.05)
    # 270 degrees corresponds to 4 ms (duty cycle 0.2)
    duty_cycle = 0.03 + (degrees / 270) * 0.15  # Duty cycle range from 0.05 to 0.2
    print(duty_cycle)
    servo_pin.value = duty_cycle

def set_raw_position(value):
    duty_cycle = 0.0 + value
    print(duty_cycle)
    servo_pin.value = duty_cycle

# Oscillating the servo between 0 and 270 degrees
try:
    while True:
        # Move to 0 degrees (start position)
        set_raw_position(0.02)
        print('0 degrees')
        sleep(3)

        # Move to 270 degrees (end position)
        set_raw_position(0.139)
        print('270 degrees')
        sleep(3)

except KeyboardInterrupt:
    servo_pin.off()  # Turn off PWM output when exiting
