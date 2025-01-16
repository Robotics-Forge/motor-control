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

#This script mirrors the servos but applies multi-turn mode to the follower servo to prevent these distance limits, the new algo also helps to do so. 

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

        leader_id = 27    # The servo we're following
        follower_id = 37  # The servo that will mirror
        print(f"Leader servo ID: {leader_id}, Follower servo ID: {follower_id}")

        # Disable torque on both servos
        print("Disabling torque...")
        tuna.writeReg(follower_id, 40, 0)
        tuna.writeReg(leader_id, 40, 0)
        time.sleep(0.1)

        # Set both servos to multi-turn mode
        print("Setting multi-turn mode...")
        tuna.writeReg(follower_id, 33, 0)  # 0 = multi-turn mode
        tuna.writeReg(leader_id, 33, 0)    # 0 = multi-turn mode
        time.sleep(0.1)

        # Re-enable torque ONLY on follower
        print("Enabling torque on follower...")
        tuna.writeReg(follower_id, 40, 1)
        time.sleep(0.1)

        # Move follower to middle position (2048)
        print("Moving to middle position...")
        middle_position = 2048
        tuna.writeReg(follower_id, 42, middle_position)
        time.sleep(1)  # Give it time to reach position

        print("\nStarting position mirroring (Press Ctrl+C to stop)...")
        last_position = None
        accumulated_position = middle_position  # Start from middle position
        initial_position = tuna.readReg(leader_id, 56)
        offset = middle_position - initial_position  # Calculate offset
        
        while True:
            # Read position from leader servo
            current_position = tuna.readReg(leader_id, 56)
            
            if last_position is not None:
                # Calculate the difference, handling wraparound
                diff = current_position - last_position
                if diff > 2048:  # More than half rotation clockwise wraparound
                    diff -= 4096
                elif diff < -2048:  # More than half rotation counter-clockwise wraparound
                    diff += 4096
                
                # Update accumulated position with offset
                accumulated_position += diff
                
                # Apply position to follower servo
                tuna.writeReg(follower_id, 42, accumulated_position)
                print(f"Leader: {current_position}, Follower: {accumulated_position}, Diff: {diff}")
            
            last_position = current_position
            time.sleep(0.01)  # Small delay to prevent overwhelming the bus

    except KeyboardInterrupt:
        print("\nStopping mirroring...")
        
    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
