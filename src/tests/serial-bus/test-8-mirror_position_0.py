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

        # Scan for connected servos
        print("Scanning for connected servos...")
        connected_servos = []
        for id in range(10):
            print(f"Checking ID {id}...", end=' ')
            result = tuna.readReg(id, 5)
            if result is not None:
                connected_servos.append(id)
                print("Found!")
            else:
                print("Not found")
            time.sleep(0.1)

        if len(connected_servos) != 2:
            print("\nError: Need exactly 2 servos connected!")
            return

        print(f"\nFound servos with IDs: {connected_servos}")

        # Enable torque for both servos (register 40)
        print("\nEnabling servos...")
        tuna.writeReg(1, 40, 1)  # Enable servo 1
        tuna.writeReg(2, 40, 1)  # Enable servo 2
        time.sleep(0.5)

        # Read initial positions
        pos1 = tuna.readReg(1, 56)  # Position of servo 1
        pos2 = tuna.readReg(2, 56)  # Position of servo 2
        print(f"\nInitial positions:")
        print(f"Servo #1: {pos1}")
        print(f"Servo #2: {pos2}")

        # Move servo 2 to servo 1's position
        print(f"\nMoving servo #2 to match servo #1's position ({pos1})...")
        tuna.writeReg(2, 42, pos1)  # Using register 42 for target position
        
        # Wait and verify position
        print("Waiting for movement to complete...")
        time.sleep(2)
        current_pos = tuna.readReg(2, 56)
        print(f"Servo #2 current position: {current_pos}")
        
        # Wait 5 seconds
        print("Holding position for 5 seconds...")
        time.sleep(5)

        # Move servo 2 back to original position
        print(f"\nMoving servo #2 back to original position ({pos2})...")
        tuna.writeReg(2, 42, pos2)  # Using register 42 for target position
        
        # Wait and verify return position
        print("Waiting for return movement to complete...")
        time.sleep(2)
        final_pos = tuna.readReg(2, 56)
        print(f"Servo #2 final position: {final_pos}")

    finally:
        # Disable torque before closing
        print("\nDisabling servos...")
        try:
            tuna.writeReg(1, 40, 0)
            tuna.writeReg(2, 40, 0)
        except:
            pass
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
