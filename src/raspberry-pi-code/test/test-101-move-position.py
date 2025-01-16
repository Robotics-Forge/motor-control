import os
import sys
import time

# Add the feetech-tuna directory dynamically to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_tuna_path = os.path.abspath(os.path.join(current_dir, '../..', 'feetech-tuna'))
sys.path.append(feetech_tuna_path)
from feetech_tuna import FeetechTuna
import serial.tools.list_ports

SERVO_ID = 1  # Servo ID to move
TARGET_POSITION = 1000  # Target position

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

        # Read initial position
        initial_position = tuna.readReg(SERVO_ID, 56)
        print(f"Initial position: {initial_position}")

        # Enable torque
        print("Enabling torque...")
        tuna.writeReg(SERVO_ID, 40, 1)
        time.sleep(0.1)

        # Move to target position
        print(f"Moving to position {TARGET_POSITION}...")
        tuna.writeReg(SERVO_ID, 42, TARGET_POSITION)

        # Monitor position until reached or timeout
        print("Monitoring position...")
        start_time = time.time()
        while time.time() - start_time < 5:  # 5 second timeout
            current_position = tuna.readReg(SERVO_ID, 56)
            print(f"Current position: {current_position}")

            # Check if we're close enough to target
            if abs(current_position - TARGET_POSITION) < 5:
                print("Target position reached!")
                break

            time.sleep(0.2)  # Small delay between readings

        # Final position check
        final_position = tuna.readReg(SERVO_ID, 56)
        print(f"Final position: {final_position}")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    finally:
        tuna.closeSerialPort()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
