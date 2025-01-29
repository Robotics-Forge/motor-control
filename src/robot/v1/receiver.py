import socket
import serial.tools.list_ports
import sys
import os

# Add the motor-control directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'motor-control'))
sys.path.append(path)

from motor_control import MotorController

# Network configuration
HOST = '192.168.1.171'
PORT = 12345

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

    controller = MotorController()
    try:
        # Connect to serial port
        if not controller.connect(port=selected_port, baudrate=1000000):
            print(f"Failed to open serial port {selected_port}.")
            return

        # Initialize servos
        controller.initialize_servos()

        # Set all servos to starting positions
        controller.set_servo_positions_to_starting_positions()
        return

        # Get current positions of slave servos as their baseline
        slave_baselines = controller.get_servo_positions(controller.get_follower_ids())
        master_baselines = None

        print(f"Receiver listening on {HOST}:{PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)

            conn, addr = server_socket.accept()
            print(f"Connection established with {addr}")

            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                try:
                    commands = eval(data)  # Replace with `json.loads` if using JSON
                    print(f"Received commands: {commands}")

                    # Initialize master baselines on the first command received
                    if master_baselines is None:
                        master_baselines = {
                            controller.get_leader_id(follower_id): position
                            for follower_id, position in commands.items()
                        }

                    # Update follower servos based on deltas
                    for follower_id, follower_new_position in commands.items():
                        leader_id = controller.get_leader_id(follower_id)
                        if leader_id is None:
                            continue

                        controller.update_follower_position(
                            follower_id=follower_id,
                            follower_position=follower_new_position,
                            follower_baseline=slave_baselines[follower_id],
                            leader_baseline=master_baselines[leader_id]
                        )

                except Exception as e:
                    print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        controller.disconnect()

if __name__ == "__main__":
    main()
