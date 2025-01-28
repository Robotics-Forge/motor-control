import os
import sys
import time
from typing import Dict, List, Set, Tuple

# Add the feetech-tuna directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feetech-tuna'))
sys.path.append(path)
from feetech_tuna import FeetechTuna

# Constants
SERVO_PAIRS: List[Tuple[int, int]] =
[
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
    (17, 37),
    (18, 38)
]

REVERSED_MOTORS: Set[int] = {26, 36, 27, 37}

MULTIPLIER_MAP: Dict[int, float] = {
    24: 4, 25: 4, 26: 4, 27: 4,
    34: 4, 35: 4, 36: 4, 37: 4,
}
DEFAULT_MULTIPLIER: float = 1.0

# Register addresses
TORQUE_ENABLE_REG = 40
MODE_REG = 33
POSITION_REG = 56
GOAL_POSITION_REG = 42

class MotorController:

    # Initialization Functions
    def __init__(self):
        self.tuna = FeetechTuna()
        self._connected = False

    def connect(self, port: str, baudrate: int = 1000000) -> bool:
        """Connect to the serial port."""
        self._connected = self.tuna.openSerialPort(port=port, baudrate=baudrate)
        return self._connected

    def disconnect(self) -> None:
        """Disconnect from the serial port."""
        if self._connected:
            self.tuna.closeSerialPort()
            self._connected = False

    def initialize_servos(self) -> None:
        """Initialize all leader and follower servos in multi-turn mode."""
        print("Initializing all servos in multi-turn mode...")
        for leader_id, follower_id in SERVO_PAIRS:
            try:
                # Disable torque
                self.tuna.writeReg(follower_id, TORQUE_ENABLE_REG, 0)
                self.tuna.writeReg(leader_id, TORQUE_ENABLE_REG, 0)

                # Set multi-turn mode
                self.tuna.writeReg(follower_id, MODE_REG, 0)
                self.tuna.writeReg(leader_id, MODE_REG, 0)

                # Enable torque for followers only
                self.tuna.writeReg(follower_id, TORQUE_ENABLE_REG, 1)
                print(f"Initialized Leader {leader_id} (torque off), Follower {follower_id} (torque on)")
            except Exception as e:
                print(f"Critical: Failed to initialize pair {leader_id}-{follower_id}: {e}")

    # ID Functions
    def get_ids(self) -> List[int]:
        """Get all IDs of the servos."""
        return [leader_id for leader_id, _ in SERVO_PAIRS] + [follower_id for _, follower_id in SERVO_PAIRS]

    def get_leader_ids(self) -> List[int]:
        """Get all leader IDs."""
        return [leader_id for leader_id, _ in SERVO_PAIRS]

    def get_follower_ids(self) -> List[int]:
        """Get all follower IDs."""
        return [follower_id for _, follower_id in SERVO_PAIRS]

    def get_leader_id(self, follower_id: int) -> int:
        """Get the leader ID for a given follower ID."""
        return next((pair[0] for pair in SERVO_PAIRS if pair[1] == follower_id), None)

    def get_follower_id(self, leader_id: int) -> int:
        """Get the follower ID for a given leader ID."""
        return next((pair[1] for pair in SERVO_PAIRS if pair[0] == leader_id), None)

    # Position Functions
    def get_servo_positions(self, servo_ids: List[int]) -> Dict[int, int]:
        """Get current positions for the specified servo IDs."""
        return {
            servo_id: self.tuna.readReg(servo_id, POSITION_REG) or 2048
            for servo_id in servo_ids
        }

    def update_follower_position(
        self,
        leader_id: int,
        leader_position: int,
        leader_baseline: int,
        follower_baseline: int
    ) -> Tuple[bool, Dict]:
        """
        Update a single follower based on leader movement.

        Args:
            leader_id: ID of the leader servo
            leader_position: Current position of the leader
            leader_baseline: Baseline position of the leader
            follower_baseline: Baseline position of the follower

        Returns:
            Tuple of (success, details_dict)
        """
        follower_id = next(
            (pair[1] for pair in SERVO_PAIRS if pair[0] == leader_id), None
        )
        if follower_id is None:
            return False, {"error": f"No follower servo mapped to Leader {leader_id}"}

        # Calculate delta with wraparound handling
        range_max = 4096
        half_range = range_max // 2
        delta = leader_position - leader_baseline

        # Adjust for wraparound
        if delta > half_range:
            delta -= range_max
        elif delta < -half_range:
            delta += range_max

        # Apply direction and scaling
        if follower_id in REVERSED_MOTORS:
            delta *= -1

        multiplier = MULTIPLIER_MAP.get(follower_id, DEFAULT_MULTIPLIER)
        scaled_delta = delta * multiplier

        # Calculate and clamp new position
        new_position = max(0, min(4095, follower_baseline + scaled_delta))

        # Move the follower servo
        success = self.tuna.writeReg(follower_id, GOAL_POSITION_REG, int(new_position))

        return success, {
            'follower_id': follower_id,
            'new_position': new_position,
            'delta': delta,
            'scaled_delta': scaled_delta
        }
