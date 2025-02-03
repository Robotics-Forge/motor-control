import socket
import serial.tools.list_ports
import sys
import os
import time
from ast import literal_eval

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

def process_messages(buffer):
    """Process complete messages from the buffer and return remaining buffer content."""
    messages = []
    while '\n' in buffer:
        message, buffer = buffer.split('\n', 1)
        try:
            command = literal_eval(message)
            messages.append(command)
        except Exception as e:
            print(f"Error parsing message: {e}, buffer: {buffer}")
    return messages, buffer

def process_command(controller, command, leader_baselines, follower_baselines):
    """Process a single command message and update servo positions."""
    # Handle RESET command
    if command == "RESET" or (isinstance(command, dict) and command.get("all") == "RESET"):
        print("RESET command received")
        follower_baselines = controller.set_follower_servo_positions_to_starting_positions()
        leader_baselines = { # Reset leader baselines
            leader_id: position
            for leader_id, position in command.items()
        }
        return (leader_baselines, follower_baselines)

    # Initialize leader baselines on the first command received
    if leader_baselines is None:
        return ({
            leader_id: position
            for leader_id, position in command.items()
        }, follower_baselines)

    # Update follower servos based on deltas
    for leader_id, leader_new_position in command.items():
        if leader_id is None:
            continue

        follower_id = controller.get_follower_id(leader_id)
        success, details = controller.update_follower_position(
            follower_id=follower_id,
            follower_baseline=follower_baselines[follower_id],
            leader_position=leader_new_position,
            leader_baseline=leader_baselines[leader_id]
        )

    return (leader_baselines, follower_baselines)

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
        controller.set_follower_servo_positions_to_starting_positions()
        time.sleep(3)

        # Get current positions of follower servos as their baseline
        follower_baselines = controller.get_servo_positions(controller.get_follower_ids())
        leader_baselines = None
        buffer = ""

        print (f"Follower baselines: {follower_baselines}")
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
                    # Add received data to buffer and process messages
                    buffer += data
                    messages, buffer = process_messages(buffer)

                    # Process each complete message
                    for command in messages:
                        if time.time() % 3 < 0.1:
                            current_time = time.strftime("%H:%M:%S")

                            print()
                            print(f"[{current_time}] Received command: {command}")

                            # Print the current positions of the servos
                            print(f"Current positions: {controller.get_servo_positions(controller.get_follower_ids())}")
                            print()

                        leader_baselines, follower_baselines = process_command(
                            controller,
                            command,
                            leader_baselines,
                            follower_baselines
                        )

                except Exception as e:
                    print(f"Error in main loop: {e}")
                    buffer = ""  # Clear buffer on error

    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        controller.disconnect()

if __name__ == "__main__":
    main()
