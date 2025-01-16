import sys
import os


###
# In order to run this script, you need to have the Feetech TUNA library installed.
# We also MUST CHANGE THE IDS OF EACH SERVO IN THE SCRIPT
# IF WE DONT DO THIS, NOTHING WILL WORK AND IT WON't DETECT THE SERVO
# THIS IS AN ATROCIOUS DESIGN DECISION SO MAKE SURE TO CHANGE THE IDS BEFORE RUNNING THE SCRIPT
#
# ID CHANGE CAN BE DONE BY RUNNING ANOTHER SCRIPT ASK THE AI FOR HELP WITH THAT
###

# Add the path to the Feetech TUNA library
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_path = os.path.join(current_dir, '..', '..', 'feetech-tuna')
sys.path.append(feetech_path)

from feetech_tuna import FeetechTuna
import time

def main():
    tuna = FeetechTuna()

    try:
        if not tuna.openSerialPort(port='COM4', baudrate=1000000):
            print("Failed to open port")
            return

        servo_id = 1
        print(f"Using servo ID: {servo_id}")

        # Set to wheel mode
        print("Setting wheel mode...")
        result = tuna.packetHandler.WheelMode(servo_id)
        print(f"Wheel mode result: {result}")
        time.sleep(0.1)

        # Set speed for continuous rotation
        print("\nStarting rotation...")
        tuna.writeReg(servo_id, 46, 2048)  # Positive speed for clockwise rotation
        time.sleep(6)  # Wait for three full rotations

        # Stop rotation
        print("\nStopping rotation...")
        tuna.writeReg(servo_id, 46, 0)
        time.sleep(0.1)

    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
