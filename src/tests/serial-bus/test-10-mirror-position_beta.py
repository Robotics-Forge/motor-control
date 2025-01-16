import sys
import os
import time


#This is the beta version of the servo movement program that sort of worked but theres still issues with the position limits

# Add the path to the Feetech TUNA library
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_path = os.path.join(current_dir, '..', '..', 'feetech-tuna')
sys.path.append(feetech_path)

from feetech_tuna import FeetechTuna

def main():
    tuna = FeetechTuna()
    master_ids = [24, 25, 26, 27]
    slave_ids = [34, 35, 36, 37]
    multipliers = [-18, -9, -9, -9]  # -18x for first pair, -9x for all others
    
    # Track both last and accumulated positions
    last_positions = {}
    accumulated_positions = {}
    middle_position = 2048

    try:
        if not tuna.openSerialPort(port='COM5', baudrate=1000000):
            print("Failed to open port")
            return

        # Setup servos
        print("\nSetting up servos...")
        for master_id, slave_id in zip(master_ids, slave_ids):
            # Disable torque on all servos temporarily
            tuna.writeReg(master_id, 40, 0)
            tuna.writeReg(slave_id, 40, 0)
            time.sleep(0.1)

            # Set multi-turn mode
            tuna.writeReg(master_id, 33, 0)  # 0 = multi-turn mode
            tuna.writeReg(slave_id, 33, 0)
            time.sleep(0.1)

            # Enable torque only on slaves
            tuna.writeReg(slave_id, 40, 1)
            time.sleep(0.1)

            # Initialize tracking variables
            last_positions[master_id] = tuna.readReg(master_id, 56)
            accumulated_positions[slave_id] = middle_position

            # Move slave to middle position
            tuna.writeReg(slave_id, 42, middle_position)
            time.sleep(0.1)

        print("\nReady! Move master servos:")
        print("24 -> 34 (18x movement)")
        print("25 -> 35 (9x movement)")
        print("26 -> 36 (9x movement)")
        print("27 -> 37 (9x movement)")
        
        while True:
            for master_id, slave_id, multiplier in zip(master_ids, slave_ids, multipliers):
                # Read position from master servo
                current_position = tuna.readReg(master_id, 56)
                if current_position is None:
                    continue

                if last_positions[master_id] is not None:
                    # Calculate the difference, handling wraparound
                    diff = current_position - last_positions[master_id]
                    if diff > 2048:  # More than half rotation clockwise wraparound
                        diff -= 4096
                    elif diff < -2048:  # More than half rotation counter-clockwise wraparound
                        diff += 4096
                    
                    # Update accumulated position with multiplier
                    accumulated_positions[slave_id] += (diff * multiplier)
                    
                    # Apply position to slave servo
                    tuna.writeReg(slave_id, 42, int(accumulated_positions[slave_id]))
                    print(f"\rM{master_id}: {last_positions[master_id]}->{current_position} (Δ{diff}) | "
                          f"S{slave_id}: {accumulated_positions[slave_id]} (Δ{diff * multiplier})", end='')
                
                last_positions[master_id] = current_position
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Disable torque on all servos
        for id in master_ids + slave_ids:
            tuna.writeReg(id, 40, 0)
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
