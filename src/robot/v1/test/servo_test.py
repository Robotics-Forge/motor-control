import os
import sys
import time
import serial.tools.list_ports

# Add the motor-control directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'motor-control'))
sys.path.append(path)

from motor_control import MotorController

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
    # Initialize controller and connect to serial port
    selected_port = select_serial_port()
    if not selected_port:
        return

    controller = MotorController()
    try:
        # Connect to serial port
        if not controller.connect(port=selected_port, baudrate=1000000):
            print(f"Failed to open serial port {selected_port}.")
            return

        # Initialize servos
        controller.initialize_servos()

        servo_id = 20
        positions = [4095, 2048, 4095]  # The positions we want to cycle through

        print(f"Starting position movement test for servo {servo_id}")

        for position in positions:
            print(f"Moving to position: {position}")
            controller.set_servo_positions({servo_id: position})
            time.sleep(3)  # Wait for 2 seconds at each position

            # Print current position
            current_pos = controller.get_servo_positions([servo_id])
            print(f"Current position: {current_pos}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()
        print("Test completed")

if __name__ == "__main__":
    main()
