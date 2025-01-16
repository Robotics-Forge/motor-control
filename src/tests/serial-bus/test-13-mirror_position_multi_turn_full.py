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

        # Define servo pairs (leader_id, follower_id)
        servo_pairs = [
            (24, 34),
            (25, 35),
            (26, 36),
            (27, 37)
        ]

        # Initialize all servos
        print("Initializing all servos...")
        for leader_id, follower_id in servo_pairs:
            print(f"Setting up pair - Leader: {leader_id}, Follower: {follower_id}")
            
            # Disable torque
            tuna.writeReg(follower_id, 40, 0)
            tuna.writeReg(leader_id, 40, 0)
            
            # Set multi-turn mode
            tuna.writeReg(follower_id, 33, 0)
            tuna.writeReg(leader_id, 33, 0)
            
            # Re-enable torque only on follower
            tuna.writeReg(follower_id, 40, 1)
            time.sleep(0.1)

        # Initialize tracking variables for each servo pair
        middle_position = 2048
        servo_states = {}
        for leader_id, follower_id in servo_pairs:
            # Move each follower to middle position
            tuna.writeReg(follower_id, 42, middle_position)
            
            # Initialize tracking state for this pair
            initial_position = tuna.readReg(leader_id, 56)
            servo_states[leader_id] = {
                'last_position': None,
                'accumulated_position': middle_position,
                'follower_id': follower_id
            }
        
        time.sleep(1)  # Give servos time to reach position
        
        print("\nStarting position mirroring (Press Ctrl+C to stop)...")
        while True:
            for leader_id, state in servo_states.items():
                follower_id = state['follower_id']
                try:
                    current_position = tuna.readReg(leader_id, 56)
                    if current_position is None:  # Handle failed reads
                        print(f"Failed to read from servo {leader_id}, skipping cycle")
                        continue
                    
                    if state['last_position'] is not None:
                        # Calculate the difference, handling wraparound
                        diff = current_position - state['last_position']
                        if diff > 2048:
                            diff -= 4096
                        elif diff < -2048:
                            diff += 4096
                        
                        # Update accumulated position
                        state['accumulated_position'] += diff
                        
                        # Try to write to follower, handle potential failures
                        write_success = tuna.writeReg(follower_id, 42, state['accumulated_position'])
                        if write_success:
                            print(f"Pair {leader_id}-{follower_id}: Leader: {current_position}, "
                                  f"Follower: {state['accumulated_position']}, Diff: {diff}")
                        else:
                            print(f"Failed to write to follower {follower_id}")
                    
                    state['last_position'] = current_position
                except Exception as e:
                    print(f"Error with servo pair {leader_id}-{follower_id}: {str(e)}")
                    continue
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping mirroring...")
        
    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
