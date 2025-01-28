import serial.tools.list_ports
import time
import sys
import os
import socket
from pynput import keyboard

# Add the motor-control directory to the path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'motor-control'))
sys.path.append(path)

# Import MotorController after adding to path
from motor_control import MotorController

# Network configuration
RECEIVER_IP = "192.168.1.171"
RECEIVER_PORT = 12345

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def main():
    print("\nSelect control mode:")
    print("1: Direct Keyboard Control")
    print("2: Teleoperation Control")

    while True:
        try:
            mode = int(input("Enter mode (1 or 2): "))
            if mode in [1, 2]:
                break
            print("Invalid selection. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    controller = None
    client_socket = None

    try:
        # Initialize motor controller for both modes
        available_ports = list_serial_ports()
        if not available_ports:
            print("No available COM ports detected.")
            return

        print("Available COM ports:")
        for i, port in enumerate(available_ports):
            print(f"{i + 1}: {port}")

        port_index = int(input("Select the COM port (number): ")) - 1
        selected_port = available_ports[port_index]

        controller = MotorController()
        if not controller.connect(port=selected_port, baudrate=1000000):
            print(f"Failed to open port {selected_port}")
            return
        controller.initialize_servos()

        if mode == 2:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((RECEIVER_IP, RECEIVER_PORT))
            print(f"Connected to receiver at {RECEIVER_IP}:{RECEIVER_PORT}")

        if mode == 1:
            handle_keyboard(controller)
        else:
            handle_teleoperation(controller, client_socket)
    except KeyboardInterrupt:
        print("Stopping controller...")
    finally:
        if controller:
            controller.disconnect()
        if client_socket:
            client_socket.close()

def handle_keyboard(controller):
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
            key_char = key.char
        except AttributeError:
            return

        step_size = controller.get_step_size()

        # Define key-to-servo mappings and their position changes
        key_mappings = {
            '1': (20, controller.get_step_size(20)), 'q': (20, -controller.get_step_size(20)),
            '2': (21, controller.get_step_size(21)), 'w': (21, -controller.get_step_size(21)),
            '3': (22, controller.get_step_size(22)), 'e': (22, -controller.get_step_size(22)),
            '4': (23, controller.get_step_size(23)), 'r': (23, -controller.get_step_size(23)),
            '5': (24, controller.get_step_size(24)), 't': (24, -controller.get_step_size(24)),
            '6': (25, controller.get_step_size(25)), 'y': (25, -controller.get_step_size(25)),
            '7': (26, controller.get_step_size(26)), 'u': (26, -controller.get_step_size(26)),
            '8': (27, controller.get_step_size(27)), 'i': (27, -controller.get_step_size(27)),
            '9': (30, controller.get_step_size(30)), 'o': (30, -controller.get_step_size(30)),
            '0': (31, controller.get_step_size(31)), 'p': (31, -controller.get_step_size(31)),
            'a': (32, controller.get_step_size(32)), 'z': (32, -controller.get_step_size(32)),
            's': (33, controller.get_step_size(33)), 'x': (33, -controller.get_step_size(33)),
            'd': (34, controller.get_step_size(34)), 'c': (34, -controller.get_step_size(34)),
            'f': (35, controller.get_step_size(35)), 'v': (35, -controller.get_step_size(35)),
            'g': (36, controller.get_step_size(36)), 'b': (36, -controller.get_step_size(36)),
            'h': (37, controller.get_step_size(37)), 'n': (37, -controller.get_step_size(37)),
            'j': (38, controller.get_step_size(38)), 'm': (38, -controller.get_step_size(38)),
        }

        if key_char in key_mappings:
            servo_id, change = key_mappings[key_char]
            current_pos = controller.get_servo_positions([servo_id])[servo_id]
            new_pos = current_pos + change
            controller.set_servo_positions([servo_id], {servo_id: new_pos})

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
