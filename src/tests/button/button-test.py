from gpiozero import LED
from time import sleep

# Create an LED object connected to GPIO18
led = LED(18)

try:
    while True:
        led.on()    # Turn LED on
        sleep(1)    # Wait for 1 second
        led.off()   # Turn LED off
        sleep(1)    # Wait for 1 second

except KeyboardInterrupt:
    print("\nProgram stopped by user")
