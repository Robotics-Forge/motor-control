import os
import sys
import time
from typing import Dict, List, Set, Tuple, Optional

# Add the feetech-tuna directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feetech-tuna'))
sys.path.append(path)

# Import after adding to path
from feetech_tuna import FeetechTuna

class MotorController:

    # Constants
    SERVO_PAIRS: List[Tuple[int, int]] = [
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
        24: 3, 25: 3, 26: 3, 27: 3,
        34: 3, 35: 3, 36: 3, 37: 3,
    }
    DEFAULT_MULTIPLIER: float = 1.0

    # Register addresses
    TORQUE_ENABLE_REG = 40
    MODE_REG = 33
    POSITION_REG = 56
    GOAL_POSITION_REG = 42

    # Class constants
    STEP_SIZE = 50  # Adjust this value to control movement sensitivity

    # Keyboard mapping for follower motors
    # Format: follower_id: {'up_key': key, 'down_key': key}
    KEYBOARD_MAPPING = {
        20: {'up_key': '1', 'down_key': 'q'},  # First pair
        21: {'up_key': '2', 'down_key': 'w'},  # Second pair
        22: {'up_key': '3', 'down_key': 'e'},  # Third pair
        23: {'up_key': '4', 'down_key': 'r'},  # Fourth pair
        24: {'up_key': '5', 'down_key': 't'},  # Fifth pair
        25: {'up_key': '6', 'down_key': 'y'},  # Sixth pair
        26: {'up_key': '7', 'down_key': 'u'},  # Seventh pair
        27: {'up_key': '8', 'down_key': 'i'},  # Eighth pair
        30: {'up_key': '9', 'down_key': 'o'},  # Ninth pair
        31: {'up_key': '0', 'down_key': 'p'},  # Tenth pair
        32: {'up_key': 'a', 'down_key': 'z'},  # Eleventh pair
        33: {'up_key': 's', 'down_key': 'x'},  # Twelfth pair
        34: {'up_key': 'd', 'down_key': 'c'},  # Thirteenth pair
        35: {'up_key': 'f', 'down_key': 'v'},  # Fourteenth pair
        36: {'up_key': 'g', 'down_key': 'b'},  # Fifteenth pair
        37: {'up_key': 'h', 'down_key': 'n'},  # Sixteenth pair
        38: {'up_key': 'j', 'down_key': 'm'},  # Seventeenth pair
    }

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
        for leader_id, follower_id in self.SERVO_PAIRS:
            try:
                # Disable torque
                self.tuna.writeReg(follower_id, self.TORQUE_ENABLE_REG, 0)
                self.tuna.writeReg(leader_id, self.TORQUE_ENABLE_REG, 0)

                # Set multi-turn mode
                self.tuna.writeReg(follower_id, self.MODE_REG, 0)
                self.tuna.writeReg(leader_id, self.MODE_REG, 0)

                # Enable torque for followers only
                self.tuna.writeReg(follower_id, self.TORQUE_ENABLE_REG, 1)
                print(f"Initialized Leader {leader_id} (torque off), Follower {follower_id} (torque on)")
            except Exception as e:
                print(f"Critical: Failed to initialize pair {leader_id}-{follower_id}: {e}")

    # ID Functions
    def get_ids(self) -> List[int]:
        """Get all IDs of the servos."""
        return [leader_id for leader_id, _ in self.SERVO_PAIRS] + [follower_id for _, follower_id in self.SERVO_PAIRS]

    def get_leader_ids(self) -> List[int]:
        """Get all leader IDs."""
        return [leader_id for leader_id, _ in self.SERVO_PAIRS]

    def get_follower_ids(self) -> List[int]:
        """Get all follower IDs."""
        return [follower_id for _, follower_id in self.SERVO_PAIRS]

    def get_leader_id(self, follower_id: int) -> int:
        """Get the leader ID for a given follower ID."""
        return next((pair[0] for pair in self.SERVO_PAIRS if pair[1] == follower_id), None)

    def get_follower_id(self, leader_id: int) -> int:
        """Get the follower ID for a given leader ID."""
        return next((pair[1] for pair in self.SERVO_PAIRS if pair[0] == leader_id), None)

    # Position Functions
    def get_servo_positions(self, servo_ids: List[int]) -> Dict[int, int]:
        """Get current positions for the specified servo IDs."""
        return {
            servo_id: self.tuna.readReg(servo_id, self.POSITION_REG) or 2048
            for servo_id in servo_ids
        }

    def set_servo_positions(self, positions: Dict[int, int]) -> None:
        """Set the position for a list of servos."""
        for servo_id, position in positions.items():
            self.tuna.writeReg(servo_id, self.GOAL_POSITION_REG, position)

    def get_step_size(self, servo_id: Optional[int] = None) -> int:
        """
        Get the step size for a servo, adjusted by its multiplier if applicable.

        Args:
            servo_id: ID of the servo, or None

        Returns:
            Adjusted step size. Returns default step size if servo_id is None.
        """
        if servo_id is None:
            return self.STEP_SIZE
        multiplier = self.MULTIPLIER_MAP.get(servo_id, self.DEFAULT_MULTIPLIER)
        return int(self.STEP_SIZE * multiplier)

    # Teleoperation Functions
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
        # Find the follower_id by looking up the leader_id in SERVO_PAIRS
        follower_id = self.get_follower_id(leader_id)
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
        if follower_id in self.REVERSED_MOTORS:
            delta *= -1

        multiplier = self.MULTIPLIER_MAP.get(follower_id, self.DEFAULT_MULTIPLIER)
        scaled_delta = delta * multiplier

        # Calculate and clamp new position
        new_position = max(0, min(4095, follower_baseline + scaled_delta))

        # Move the follower servo
        success = self.tuna.writeReg(follower_id, self.GOAL_POSITION_REG, int(new_position))

        return success, {
            'follower_id': follower_id,
            'new_position': new_position,
            'delta': delta,
            'scaled_delta': scaled_delta
        }

    # Keyboard Functions
    def get_follower_for_key(self, key: str) -> Optional[int]:
        """
        Get the follower ID associated with a keyboard key.

        Args:
            key: The pressed keyboard key

        Returns:
            Follower ID if the key is mapped, None otherwise
        """
        key = key.lower()
        for follower_id, mapping in self.KEYBOARD_MAPPING.items():
            if key in [mapping['up_key'], mapping['down_key']]:
                return follower_id
        return None
