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
    # Create instance
    tuna = FeetechTuna()

    try:
        # Open port (using same settings as original code)
        if not tuna.openSerialPort(port='COM4', baudrate=1000000):
            print("Failed to open port")
            return

        # Find servos
        servos = tuna.listServos()
        if not servos or len(servos) < 2:
            print("Need at least 2 servos connected")
            return

        servo1_id = servos[0]["id"]
        servo2_id = servos[1]["id"]
        print(f"Using servo IDs: {servo1_id} and {servo2_id}")

        # Enable torque for both servos
        for servo_id in [servo1_id, servo2_id]:
            tuna.writeReg(servo_id, 40, 1)
        time.sleep(0.1)

        # Move servos to their respective positions
        print("\nMoving servos to positions...")
        tuna.writeReg(servo1_id, 42, 4000)  # First servo to 4000
        tuna.writeReg(servo2_id, 42, 2000)  # Second servo to 2000
        time.sleep(2)  # Wait for movement

        # Move both back to position 0
        print("\nMoving servos back to 0...")
        for servo_id in [servo1_id, servo2_id]:
            tuna.writeReg(servo_id, 42, 0)
        time.sleep(2)

        # Disable torque for both servos
        for servo_id in [servo1_id, servo2_id]:
            tuna.writeReg(servo_id, 40, 0)

    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
