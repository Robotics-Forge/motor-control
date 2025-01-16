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
        # Open port (using same settings as original code)
        if not tuna.openSerialPort(port='COM4', baudrate=1000000):
            print("Failed to open port")
            return

        # Find servos
        servos = tuna.listServos()
        if not servos:
            print("No servos found")
            return

        servo_id = servos[0]["id"]
        print(f"Using servo ID: {servo_id}")

        # Enable torque
        tuna.writeReg(servo_id, 40, 1)
        time.sleep(0.1)

        # Move servo to position
        print("\nMoving servo to position 4000...")
        tuna.writeReg(servo_id, 42, 4000)

        # Monitor motion parameters during movement
        print("\nMonitoring motion parameters...")
        for _ in range(10):  # Take 10 readings during motion
            position = tuna.readReg(servo_id, 56)
            velocity = tuna.readReg(servo_id, 58)
            acceleration = tuna.readReg(servo_id, 60)
            print(f"Position: {position}, Velocity: {velocity}, Acceleration: {acceleration}")
            time.sleep(0.2)

        # Move back to position 0
        print("\nMoving servo back to 0...")
        tuna.writeReg(servo_id, 42, 0)

        # Monitor motion parameters during return movement
        print("\nMonitoring return motion parameters...")
        for _ in range(10):  # Take 10 readings during motion
            position = tuna.readReg(servo_id, 56)
            velocity = tuna.readReg(servo_id, 58)
            acceleration = tuna.readReg(servo_id, 60)
            print(f"Position: {position}, Velocity: {velocity}, Acceleration: {acceleration}")
            time.sleep(0.2)

        # Disable torque
        tuna.writeReg(servo_id, 40, 0)

    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
