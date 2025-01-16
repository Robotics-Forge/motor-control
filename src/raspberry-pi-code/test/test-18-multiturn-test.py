import os
import sys
import time
# Add the feetech-tuna directory dynamically to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_tuna_path = os.path.abspath(os.path.join(current_dir, '../..', 'feetech-tuna'))
sys.path.append(feetech_tuna_path)
from feetech_tuna import FeetechTuna
import serial.tools.list_ports

# Servo ID and desired rotation configuration
SERVO_ID = 1  # Servo ID to configure and rotate
ROTATION_DEGREES = 540  # Desired rotation in degrees
DESIRED_SPEED = 682  # Adjusted speed based on observations

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

        # Initial position in multiturn mode
        initial_position = tuna.readReg(SERVO_ID, 56)
        print(f"Initial position in multiturn mode: {initial_position}")

        # Switch to wheel mode
        print("Switching to wheel mode...")
        tuna.writeReg(SERVO_ID, 33, 1)  # 1 = wheel mode

        # Set speed in wheel mode
        print("Setting speed in wheel mode...")
        tuna.writeReg(SERVO_ID, 46, DESIRED_SPEED)  # Speed register
        print(f"Speed set to {DESIRED_SPEED}.")

        # Rotate for a specified time (based on previous observations)
        rotation_time = 9  # Adjust time as needed for consistency
        print(f"Rotating for {rotation_time:.2f} seconds...")
        time.sleep(rotation_time)

        # Stop the servo
        print("Stopping servo...")
        tuna.writeReg(SERVO_ID, 46, 0)  # Stop rotation

        # Switch back to multiturn mode
        print("Switching back to multiturn mode...")
        tuna.writeReg(SERVO_ID, 33, 0)  # 0 = multiturn mode

        # Read final position
        final_position = tuna.readReg(SERVO_ID, 56)
        print(f"Final position after rotation: {final_position}")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    finally:
        tuna.closeSerialPort()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
