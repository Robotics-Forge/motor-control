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
            
            # First disable torque on both servos
            tuna.writeReg(follower_id, 40, 0)
            tuna.writeReg(leader_id, 40, 0)
            time.sleep(0.1)
            
            # Set position mode
            tuna.writeReg(follower_id, 33, 0)
            tuna.writeReg(leader_id, 33, 0)
            time.sleep(0.1)
            
            # Only enable torque on follower, leave leader free to move
            tuna.writeReg(follower_id, 40, 1)
            time.sleep(0.1)

        # Initialize tracking variables for each servo pair
        servo_states = {}
        for leader_id, follower_id in servo_pairs:
            # Read the current position of the follower
            current_follower_pos = tuna.readReg(follower_id, 56)
            if current_follower_pos is not None:
                print(f"Follower {follower_id} starting position: {current_follower_pos}")
                tuna.writeReg(follower_id, 42, current_follower_pos)
            
            # Initialize tracking state for this pair
            initial_position = tuna.readReg(leader_id, 56)
            servo_states[leader_id] = {
                'last_position': initial_position,
                'accumulated_position': current_follower_pos,
                'follower_id': follower_id,
                # Increased multiplier to get closer to 1:1 ratio
                'multiplier': 3.0 if leader_id == 24 else 1.0  # 3x multiplier for servo 24-34 pair
            }
        
        time.sleep(1)  # Give servos time to stabilize
        
        print("\nStarting position mirroring (Press Ctrl+C to stop)...")
        while True:
            for leader_id, state in servo_states.items():
                follower_id = state['follower_id']
                try:
                    current_position = tuna.readReg(leader_id, 56)
                    print(f"Read position from leader {leader_id}: {current_position}")
                    
                    if current_position is None:
                        print(f"Failed to read from servo {leader_id}, skipping cycle")
                        continue
                    
                    if state['last_position'] is not None:
                        # Calculate the difference, handling wraparound
                        diff = current_position - state['last_position']
                        if diff > 2048:
                            diff -= 4096
                        elif diff < -2048:
                            diff += 4096
                        
                        # Update accumulated position (in opposite direction for mirroring)
                        # Apply multiplier to the difference and convert to integer
                        state['accumulated_position'] -= int(diff * state['multiplier'])
                        
                        # Keep accumulated position within valid range
                        if state['accumulated_position'] > 4095:
                            state['accumulated_position'] = 4095
                        elif state['accumulated_position'] < 0:
                            state['accumulated_position'] = 0
                        
                        # Try to write to follower
                        write_success = tuna.writeReg(follower_id, 42, int(state['accumulated_position']))
                        if write_success:
                            actual_position = tuna.readReg(follower_id, 56)
                            print(f"Pair {leader_id}-{follower_id}: Leader: {current_position}, "
                                  f"Follower target: {state['accumulated_position']}, "
                                  f"Follower actual: {actual_position}, Diff: {diff}")
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
