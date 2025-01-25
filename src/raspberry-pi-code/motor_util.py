import time
import sys
import os

# Add the feetech-tuna directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feetech-tuna'))
sys.path.append(path)
from feetech_tuna import FeetechTuna

# Define servo pairs
SERVO_PAIRS = [
    (40, 20),
    (1, 21),
    (2, 22),
    (3, 23),
    (4, 24),
    (5, 25),
    (6, 26),
    (7, 27),
    (10, 30),
    (11, 31),
    (12, 32),
    (13, 33),
    (14, 34),
    (15, 35),
    (16, 36),
    (17, 37)
    (18, 38)
]

# Motors to reverse directions
REVERSED_MOTORS = {
    26, 36, 27, 37  # Reverse direction for these follower motors
}

def initialize_servos(tuna):
    """
    Initialize all leader and follower servos in multi-turn mode.
    Disable torque for leaders and enable it for followers.
    """
    print("Initializing all servos in multi-turn mode...")
    for leader_id, follower_id in SERVO_PAIRS:
        try:
            # Disable torque
            tuna.writeReg(follower_id, 40, 0)
            tuna.writeReg(leader_id, 40, 0)

            # Set multi-turn mode (register 33 = 0 for multi-turn)
            tuna.writeReg(follower_id, 33, 0)
            tuna.writeReg(leader_id, 33, 0)

            # Enable torque for followers only
            tuna.writeReg(follower_id, 40, 1)
            print(f"Initialized Leader {leader_id} (torque off), Follower {follower_id} (torque on)")
        except Exception as e:
            print(f"Critical: Failed to initialize pair {leader_id}-{follower_id}: {e}")

def get_servo_positions(tuna):
    """
    Get current positions of all leader servos in multi-turn mode.
    """
    positions = {}
    print("\n=== Reading Leader Positions ===")
    for leader_id, _ in SERVO_PAIRS:
        try:
            # Read multi-turn position
            position = tuna.readReg(leader_id, 56)  # Replace 56 with correct register for multi-turn position if needed
            print(f"Leader {leader_id} position: {position}")
            if position is not None:
                positions[leader_id] = position
        except Exception as e:
            print(f"Warning: Failed to read position for leader {leader_id}: {e}")
    return positions

def update_follower_positions(tuna, commands, baselines, follower_positions):
    """
    Update follower servos based on received commands, relative to baseline positions.
    :param tuna: FeetechTuna instance.
    :param commands: Dictionary of leader positions {leader_id: position}.
    :param baselines: Dictionary of baseline positions for leaders and followers.
    :param follower_positions: Current positions of followers.
    """
    for leader_id, position in commands.items():
        follower_id = next((pair[1] for pair in SERVO_PAIRS if pair[0] == leader_id), None)
        if follower_id is None:
            continue

        try:
            # Calculate delta from baseline for the leader
            delta = position - baselines['leader'][leader_id]

            # Reverse delta for specific follower motors
            if follower_id in REVERSED_MOTORS:
                delta *= -1

            # Calculate the new position for the follower based on its baseline
            new_follower_position = baselines['follower'][follower_id] + delta

            # Clamp position within valid bounds
            new_follower_position = max(0, min(4095, new_follower_position))

            # Send position to follower servo
            success = tuna.writeReg(follower_id, 42, int(new_follower_position))
            if success:
                print(f"Follower {follower_id} moved to {new_follower_position} (Delta: {delta})")
                follower_positions[follower_id] = new_follower_position  # Update current position
            else:
                print(f"Failed to move Follower {follower_id}")
        except Exception as e:
            print(f"Error updating Follower {follower_id}: {e}")
