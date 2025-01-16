import sys
import os

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
        if not servos:
            print("No servos found")
            return

        servo_id = servos[0]["id"]  # Use first servo found
        print(f"Using servo ID: {servo_id}")

        # Enable torque
        tuna.writeReg(servo_id, 40, 1)  # 40 is SMS_STS_TORQUE_ENABLE
        time.sleep(0.1)

        # Move to position 4000
        print("\nMoving to position 4000...")
        tuna.writeReg(servo_id, 42, 4000)  # 42 is SMS_STS_GOAL_POSITION_L
        time.sleep(2)  # Wait for movement

        # Move back to position 0
        print("\nMoving to position 0...")
        tuna.writeReg(servo_id, 42, 0)
        time.sleep(2)

        # Disable torque
        tuna.writeReg(servo_id, 40, 0)

    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
