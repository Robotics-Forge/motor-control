import sys
import os
import time

# Add the path to the Feetech TUNA library
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_path = os.path.join(current_dir, '..', '..', 'feetech-tuna')
sys.path.append(feetech_path)

from feetech_tuna import FeetechTuna

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
            time.sleep(0.05)

        if 1 not in connected_servos:
            print("\nError: Servo ID 1 (master) not found!")
            return

        print(f"\nFound {len(connected_servos)} servos with IDs: {connected_servos}")

        # Enable torque for all servos EXCEPT servo 1
        print("\nSetting up servos...")
        for id in connected_servos:
            if id != 1:  # Only enable torque on non-master servos
                tuna.writeReg(id, 40, 1)  # Enable torque
                tuna.writeReg(id, 41, 0)   # Set acceleration to 0 for faster response
            else:
                tuna.writeReg(id, 40, 0)   # Disable torque on master
            time.sleep(0.02)  # Minimal delay between commands

        # Get initial position and sync all servos
        last_position = tuna.readReg(1, 56)
        for id in connected_servos:
            if id != 1:
                tuna.writeReg(id, 42, last_position)
                time.sleep(0.02)

        print("\nReady! Move servo 1 and others will follow.")
        print("(Press Ctrl+C to stop)")

        while True:
            current_position = tuna.readReg(1, 56)
            
            # Reduced threshold for more responsive mirroring
            if abs(current_position - last_position) > 2:  # Reduced from 5 to 2
                for id in connected_servos:
                    if id != 1:
                        tuna.writeReg(id, 42, current_position)
                last_position = current_position
            
            time.sleep(0.01)  # Minimal delay while still allowing system to function

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # Cleanup
        for id in connected_servos:
            tuna.writeReg(id, 40, 0)
            time.sleep(0.02)
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
