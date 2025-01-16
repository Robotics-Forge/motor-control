import os  # Ensure this is imported
import serial.tools.list_ports
from motor_util import initialize_servos
from feetech_tuna import FeetechTuna

INPUT_FILE = "robot_starting_position.csv"

def set_robot_position():
    if not os.path.exists(INPUT_FILE):
        print(f"Position file '{INPUT_FILE}' not found. Ensure you run the capture script first.")
        return

    tuna = FeetechTuna()
    try:
        # List available serial ports and allow the user to select one
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if not available_ports:
            print("No available serial ports detected.")
            return

        print("Available serial ports:")
        for i, port in enumerate(available_ports):
            print(f"{i + 1}: {port}")

        port_index = int(input("Select the serial port (number): ")) - 1
        selected_port = available_ports[port_index]

        # Open the selected port
        print(f"Opening serial port: {selected_port}")
        if not tuna.openSerialPort(port=selected_port, baudrate=1000000):
            print(f"Failed to open serial port {selected_port}.")
            return

        print("Serial port opened successfully")

        # Initialize servos (if necessary)
        initialize_servos(tuna)

        # Load positions from the CSV file
        positions = {}
        with open(INPUT_FILE, "r") as file:
            next(file)  # Skip the header
            for line in file:
                servo_id, position = line.strip().split(",")
                positions[int(servo_id)] = int(position)

        # Set servos to the captured positions
        for servo_id, position in positions.items():
            success = tuna.writeReg(servo_id, 42, position)
            if success:
                print(f"Servo {servo_id} moved to position {position}.")
            else:
                print(f"Failed to move servo {servo_id} to position {position}.")

        print("Robot moved to the captured starting position.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Safely close the port
        try:
            tuna.closeSerialPort()
        except Exception as e:
            print(f"Error closing port: {e}")

if __name__ == "__main__":
    set_robot_position()
