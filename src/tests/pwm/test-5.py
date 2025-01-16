from gpiozero import PWMOutputDevice
from time import sleep

control_servo_pin = PWMOutputDevice(17, frequency=50)  # 50 Hz PWM for servo

try:
    while True:
        control_pin_value = control_servo_pin.value
        print(control_pin_value)
        
        sleep(3)
        control_servo_pin.value = 0.02
        sleep(3)
        control_servo_pin.value = 0.13

except KeyboardInterrupt:
    # servo_pin.off()  # Turn off PWM output when exiting
    control_servo_pin.off()
