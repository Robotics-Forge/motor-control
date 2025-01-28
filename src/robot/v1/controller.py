import serial.tools.list_ports
import time
import sys
import os
import socket
from pynput import keyboard

# Add the motor-control directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'motor-control'))
sys.path.append(path)

from motor_control import MotorController

# Network configuration
RECEIVER_IP = "192.168.1.171"
RECEIVER_PORT = 12345

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def main():
    available_ports = list_serial_ports()
    if not available_ports:
        print("No available COM ports detected.")
        return

    print("Available COM ports:")
    for i, port in enumerate(available_ports):
        print(f"{i + 1}: {port}")

    port_index = int(input("Select the COM port (number): ")) - 1
    selected_port = available_ports[port_index]

    # Add control mode selection
    print("\nSelect control mode:")
    print("1: Keyboard control")
    print("2: Teleoperation")

    while True:
        try:
            mode = int(input("Enter mode (1 or 2): "))
            if mode in [1, 2]:
                break
            print("Invalid selection. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    controller = MotorController(port=selected_port, baudrate=1000000)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if not controller.connect():
            print(f"Failed to open port {selected_port}")
            return

        controller.initialize_motors()
        client_socket.connect((RECEIVER_IP, RECEIVER_PORT))
        print(f"Connected to receiver at {RECEIVER_IP}:{RECEIVER_PORT}")

        if mode == 1:
            handle_keyboard(controller, client_socket)
        else:
            handle_teleoperation(controller, client_socket)
    except KeyboardInterrupt:
        print("Stopping controller...")
    finally:
        controller.disconnect()
        client_socket.close()

def handle_keyboard(controller, client_socket):
    print("\nKeyboard Control Mode Active")
    print("Controls:")
    print("Each servo pair has an up/down key:")
    print("Servo 20: 1/q    Servo 30: 9/o")
    print("Servo 21: 2/w    Servo 31: 0/p")
    print("Servo 22: 3/e    Servo 32: a/z")
    print("Servo 23: 4/r    Servo 33: s/x")
    print("Servo 24: 5/t    Servo 34: d/c")
    print("Servo 25: 6/y    Servo 35: f/v")
    print("Servo 26: 7/u    Servo 36: g/b")
    print("Servo 27: 8/i    Servo 37: h/n")
    print("Servo 38: j/m")

    def on_press(key):
        try:
            # Convert the key to string format
            key_char = key.char
        except AttributeError:
            # Special keys that don't have a char representation
            return

        # Get the next positions based on the key press
        follower_ids = controller.get_follower_ids()
        new_positions = controller.get_next_servo_positions(follower_ids, key_char)

        # Send the new positions to the client
        client_socket.sendall(str(new_positions).encode('utf-8'))

    # Set up keyboard listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def handle_teleoperation(controller, client_socket):
    print("\nTeleoperation Mode")
    while True:
        positions = controller.get_servo_positions(controller.get_follower_ids())
        client_socket.sendall(str(positions).encode('utf-8'))
        time.sleep(0.1)

if __name__ == "__main__":
    main()
