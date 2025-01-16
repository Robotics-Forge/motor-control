import os
import sys
import time
# Dynamically add the feetech-tuna directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_tuna_path = os.path.abspath(os.path.join(current_dir, '../..', 'feetech-tuna'))
sys.path.append(feetech_tuna_path)
import serial.tools.list_ports
from feetech_tuna import FeetechTuna

# Servo ID
SERVO_ID = 1  # Servo ID to configure and move
TARGET_POSITION = 4000  # Target position for the servo in multiturn mode

def list_serial_ports():
    """List all available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def select_serial_port():
    """Prompt user to select a serial port from available options."""
    available_ports = list_serial_ports()
    if not available_ports:
        print("No available serial ports detected. Please connect your device and try again.")
        return None

    print("Available serial ports:")
    for i, port in enumerate(available_ports):
        print(f"{i + 1}: {port}")

    while True:
        try:
            choice = int(input("Select the port to use (number): ")) - 1
            if 0 <= choice < len(available_ports):
                return available_ports[choice]
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Please enter a number.")

def is_servo_in_multiturn_mode(tuna, servo_id):
    """
    Check if the servo is in multiturn mode by reading register 33.
    """
    mode = tuna.readReg(servo_id, 33)
    if mode is not None:
        print(f"Servo {servo_id} mode register (33): {mode}")
        if mode == 0:
            print(f"Servo {servo_id} is in multiturn mode.")
            return True
        else:
            print(f"Servo {servo_id} is NOT in multiturn mode.")
            return False
    else:
        print(f"Failed to read mode register for servo {servo_id}.")
        return None

def main():
    selected_port = select_serial_port()
    if not selected_port:
        return

    tuna = FeetechTuna()
    try:
        # Open serial port
        if not tuna.openSerialPort(port=selected_port, baudrate=1000000):
            print(f"Failed to open serial port {selected_port}.")
            return

        # Check if the servo is already in multiturn mode
        is_multiturn = is_servo_in_multiturn_mode(tuna, SERVO_ID)
        if is_multiturn is None:
            print("Unable to determine multiturn mode status. Exiting.")
            return

        # If not in multiturn mode, configure the servo
        if not is_multiturn:
            # Disable torque
            print("Disabling torque...")
            tuna.writeReg(SERVO_ID, 40, 0)
            time.sleep(0.1)

            # Set multiturn mode
            print("Setting multiturn mode...")
            tuna.writeReg(SERVO_ID, 33, 0)  # 0 = multiturn mode
            time.sleep(0.1)

            # Enable torque
            print("Enabling torque...")
            tuna.writeReg(SERVO_ID, 40, 1)
            time.sleep(0.1)

            # Re-check the mode
            is_multiturn = is_servo_in_multiturn_mode(tuna, SERVO_ID)
            if not is_multiturn:
                print("Failed to set multiturn mode. Exiting.")
                return

        # Read the initial position
        initial_position = tuna.readReg(SERVO_ID, 56)
        if initial_position is not None:
            print(f"Servo {SERVO_ID} initial position: {initial_position}")
        else:
            print(f"Failed to read the initial position of servo {SERVO_ID}.")

        # Move servo to target position
        print(f"Moving servo {SERVO_ID} to position {TARGET_POSITION}...")
        success = tuna.writeReg(SERVO_ID, 42, TARGET_POSITION)
        if success:
            print(f"Servo {SERVO_ID} successfully set to position {TARGET_POSITION}.")
        else:
            print(f"Failed to set servo {SERVO_ID} to position {TARGET_POSITION}.")

        # Monitor position for confirmation
        print("Monitoring position changes...")
        for _ in range(5):  # Poll position 5 times
            current_position = tuna.readReg(SERVO_ID, 56)
            if current_position is not None:
                print(f"Servo {SERVO_ID} current position: {current_position}")
            else:
                print(f"Failed to read current position of servo {SERVO_ID}.")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    finally:
        tuna.closeSerialPort()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
