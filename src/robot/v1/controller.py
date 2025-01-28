import serial.tools.list_ports
import time
import sys
import os
import socket
from motor_control import MotorController

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feetech-tuna'))
sys.path.append(path)

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

    controller = MotorController(port=selected_port, baudrate=1000000)

    try:
        if not controller.connect():
            print(f"Failed to open port {selected_port}")
            return

        controller.initialize_motors()  # Replace initialize_servos with motor initialization

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((RECEIVER_IP, RECEIVER_PORT))
            print(f"Connected to receiver at {RECEIVER_IP}:{RECEIVER_PORT}")

            while True:
                positions = controller.get_servo_positions(controller.get_follower_ids())
                client_socket.sendall(str(positions).encode('utf-8'))
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping controller...")
    finally:
        controller.disconnect()  # Replace closeSerialPort with disconnect

if __name__ == "__main__":
    main()
