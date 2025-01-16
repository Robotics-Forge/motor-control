import serial.tools.list_ports
from motor_util import SERVO_PAIRS
from feetech_tuna import FeetechTuna

OUTPUT_FILE = "robot_starting_position.csv"

def capture_robot_position():
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

        # Read positions for all slave servos
        positions = {}
        print("\n=== Reading Slave Positions ===")
        for _, slave_id in SERVO_PAIRS:
            try:
                position = tuna.readReg(slave_id, 56)  # Replace 56 with the correct register if needed
                if position is not None:
                    positions[slave_id] = position
                    print(f"Slave {slave_id} position: {position}")
                else:
                    print(f"Failed to read position for Slave {slave_id}.")
            except Exception as e:
                print(f"Error reading position for Slave {slave_id}: {e}")

        if not positions:
            print("No positions captured. Check the servos and connections.")
            return

        # Save to CSV
        with open(OUTPUT_FILE, "w") as file:
            file.write("ServoID,Position\n")
            for servo_id, position in positions.items():
                file.write(f"{servo_id},{position}\n")

        print(f"Positions captured and saved to {OUTPUT_FILE}.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Safely close the port
        try:
            tuna.closeSerialPort()
        except Exception as e:
            print(f"Error closing port: {e}")

if __name__ == "__main__":
    capture_robot_position()
