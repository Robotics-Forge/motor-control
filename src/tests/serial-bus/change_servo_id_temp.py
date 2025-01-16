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
        print("Opening port...")
        if not tuna.openSerialPort(port='COM4', baudrate=1000000):
            print("Failed to open port")
            return

        print("Scanning for connected servo...")
        found_id = None
        for id in range(10):
            print(f"Checking ID {id}...", end=' ')
            result = tuna.readReg(id, 5)
            if result is not None:
                print("Found!")
                found_id = id
                break
            print("Not found")
            time.sleep(0.1)

        if found_id is None:
            print("\nNo servo detected! Make sure only one servo is connected.")
            return

        print(f"\nFound servo with current ID: {found_id}")
        new_id = int(input("Enter the new ID you want to set (0-253): "))
        
        if 0 <= new_id <= 253:
            print(f"Attempting to change servo ID from {found_id} to {new_id}...")
            
            # Write the new ID to register 5
            success = tuna.writeReg(found_id, 5, new_id)
            if not success:
                print("Failed to write new ID")
                return

            # Wait for the change to take effect
            time.sleep(1.0)

            # Verify the change by trying to read from the new ID
            result = tuna.readReg(new_id, 5)
            if result is not None:
                print(f"Successfully changed servo ID to {new_id}")
            else:
                print("Failed to verify new ID")
        else:
            print("Invalid ID! Must be between 0 and 253")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print("Closing port...")
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()