import os
import sys
import time
from typing import Dict, List, Set, Tuple, Optional

# Get the absolute path of the project root dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get directory of this script
feetech_tuna_root = os.path.abspath(os.path.join(current_dir, "./feetech-tuna/feetech_tuna"))  # Adjust this as needed

# Add project root to sys.path
sys.path.append(feetech_tuna_root)

# Now import your module
from feetech_tuna import FeetechTuna

class MotorController:

    # Constants
    SERVO_MAP = {
        # Leader ID: Follower ID
        40: 20,
        1: 21,
        2: 22,
        3: 23,
        4: 24,
        5: 25,
        6: 26,
        7: 27,
        10: 30,
        11: 31,
        12: 32,
        13: 33,
        14: 34,
        15: 35,
        16: 36,
        17: 37
    }

    # Create reverse mapping for easy lookup in both directions
    REVERSE_SERVO_MAP = {v: k for k, v in SERVO_MAP.items()}

    REVERSED_MOTORS: Set[int] = {24, 34, 26, 36, 27, 37, 20, 30}

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
    }

    # Add this near the other class constants
    STARTING_POSITIONS = {
        30: 4095, 31: 1100, 32: 1817, 33: 1973, 34: 1200, 35: 2194, 36: 3359, 37: 736,
        20: 4095, 21: 1500, 22: 1941, 23: 2193, 24: 2800, 25: 232, 26: 621, 27: 3211
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
        print("Initializing servos in multi-turn mode...")
        for leader_id, follower_id in self.SERVO_MAP.items():
            try:
                # Disable torque
                self.tuna.writeReg(follower_id, self.TORQUE_ENABLE_REG, 0)
                self.tuna.writeReg(leader_id, self.TORQUE_ENABLE_REG, 0)

                # Set multi-turn mode
                self.tuna.writeReg(follower_id, self.MODE_REG, 0)
                self.tuna.writeReg(leader_id, self.MODE_REG, 0)

                # Enable torque for followers only
                self.tuna.writeReg(follower_id, self.TORQUE_ENABLE_REG, 1)
            except Exception as e:
                print(f"Error initializing servos {leader_id}-{follower_id}: {e}")
        print("Servo initialization complete")

    # ID Functions
    def get_ids(self) -> List[int]:
        """Get all IDs of the servos."""
        return list(self.SERVO_MAP.keys()) + list(self.SERVO_MAP.values())

    def get_leader_ids(self) -> List[int]:
        """Get all leader IDs."""
        return list(self.SERVO_MAP.keys())

    def get_follower_ids(self) -> List[int]:
        """Get all follower IDs."""
        return list(self.SERVO_MAP.values())

    def get_leader_id(self, follower_id: int) -> Optional[int]:
        """Get the leader ID for a given follower ID."""
        return self.REVERSE_SERVO_MAP.get(follower_id)

    def get_follower_id(self, leader_id: int) -> Optional[int]:
        """Get the follower ID for a given leader ID."""
        return self.SERVO_MAP.get(leader_id)

    # Position Functions
    def get_servo_positions(self, servo_ids: List[int]) -> Dict[int, int]:
        """Get current positions for the specified servo IDs."""
        return {
            servo_id: self.tuna.readReg(servo_id, self.POSITION_REG) or self.STARTING_POSITIONS.get(servo_id, 2048)
            for servo_id in servo_ids
        }

    def set_servo_positions(self, positions: Dict[int, int]) -> None:
        """Set the position for a list of servos."""
        for servo_id, position in positions.items():
            self.tuna.writeReg(servo_id, self.GOAL_POSITION_REG, position)

    def set_servo_positions_to_starting_positions(self) -> None:
        """Set the position for a list of servos."""
        for servo_id, position in self.STARTING_POSITIONS.items():
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
        follower_id: int,
        follower_baseline: int,
        leader_position: int,
        leader_baseline: int
    ) -> Tuple[bool, Dict]:
        """
        Update a single follower based on leader movement.

        Args:
            follower_id: ID of the follower servo
            follower_baseline: Baseline position of the follower
            leader_position: Current position of the leader
            leader_baseline: Baseline position of the leader

        Returns:
            Tuple of (success, details_dict)
        """
        leader_id = self.get_leader_id(follower_id)
        if leader_id is None:
            return False, {"error": f"No leader servo mapped to Follower {follower_id}"}

        # Calculate leader's delta with wraparound handling
        range_max = 4096
        half_range = range_max // 2
        leader_delta = leader_position - leader_baseline

        # Adjust for wraparound
        if leader_delta > half_range:
            leader_delta -= range_max
        elif leader_delta < -half_range:
            leader_delta += range_max

        # Apply direction and scaling
        if follower_id in self.REVERSED_MOTORS:
            leader_delta *= -1

        multiplier = self.MULTIPLIER_MAP.get(follower_id, self.DEFAULT_MULTIPLIER)
        scaled_delta = leader_delta * multiplier

        # Calculate and clamp new follower position
        new_position = max(0, min(4095, follower_baseline + scaled_delta))

        # Record the current position as the new baseline
        previous_position = self.tuna.readReg(follower_id, self.POSITION_REG)

        # Move the follower servo
        success = self.tuna.writeReg(follower_id, self.GOAL_POSITION_REG, int(new_position))

        return success, {
            'follower_id': follower_id,
            'leader_id': leader_id,
            'follower_baseline': follower_baseline,
            'leader_baseline': leader_baseline,
            'previous_position': previous_position,
            'new_position': new_position,
            'position_delta': new_position - previous_position,
            'leader_delta': leader_delta,
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
