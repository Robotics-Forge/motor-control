import sys
import os
import time

# Add the path to the Feetech TUNA library
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_path = os.path.join(current_dir, '..', '..', 'feetech-tuna')
sys.path.append(feetech_path)

from feetech_tuna import FeetechTuna
from feetech_tuna.SCServo_Python.scservo_sdk import SMS_STS_ID  # Import the correct register address

def main():
    tuna = FeetechTuna()
    
    try:
        if not tuna.openSerialPort(port='COM5', baudrate=1000000):
            print("Failed to open port")
            return

        print("Scanning for connected servos...")
        found_servos = []
        for id in range(40):
            print(f"Checking ID {id}...", end=' ')
            result = tuna.readReg(id, SMS_STS_ID)
            if result is not None:
                found_servos.append(id)
                print("Found!")
            else:
                print("Not found")
            time.sleep(0.1)

        if not found_servos:
            print("\nNo servos detected!")
            return

        print(f"\nFound servos with IDs: {found_servos}")
        current_id = int(input("Enter servo ID to change: "))
        
        if current_id not in found_servos:
            print("Error: That ID was not found in the scan!")
            return

        new_id = int(input("Enter the new ID you want to set (0-253): "))
        
        if 0 <= new_id <= 253:
            print(f"\nWARNING: This will change the servo ID from {current_id} to {new_id}")
            confirm = input("Are you sure? (yes/no): ")
            
            if confirm.lower() == 'yes':
                # Disable torque first
                print("\nDisabling torque...")
                tuna.writeReg(current_id, 40, 0)
                time.sleep(0.5)

                # Unlock EPROM
                print("Unlocking EPROM...")
                tuna.unlockEEPROM(current_id)
                time.sleep(0.5)

                # Write the new ID
                print(f"\nChanging ID to {new_id}...")
                success = tuna.writeReg(current_id, SMS_STS_ID, new_id)
                time.sleep(1.0)  # Give it time to write

                # Lock EPROM
                print("Locking EPROM...")
                tuna.lockEEPROM(current_id)
                time.sleep(0.5)
                
                if success:
                    print("\nID change command sent successfully")
                    print("Waiting for change to take effect...")
                    time.sleep(2.0)
                    
                    # Verify the change
                    result = tuna.readReg(new_id, SMS_STS_ID)
                    if result is not None:
                        print(f"Success! Servo is now responding at ID {new_id}")
                        print("\nIMPORTANT: Leave the servo powered on for at least 5 seconds")
                        print("before disconnecting power to ensure the change is saved.")
                        time.sleep(5.0)
                    else:
                        print("Warning: Could not verify new ID")
                else:
                    print("Failed to write new ID")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("\nClosing port...")
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()