import serial.tools.list_ports
import time
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feetech-tuna'))
sys.path.append(path)
from motor_util import initialize_servos, get_servo_positions
from feetech_tuna import FeetechTuna
import socket

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

    tuna = FeetechTuna()

    try:
        if not tuna.openSerialPort(port=selected_port, baudrate=1000000):
            print(f"Failed to open port {selected_port}")
            return

        initialize_servos(tuna)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((RECEIVER_IP, RECEIVER_PORT))
            print(f"Connected to receiver at {RECEIVER_IP}:{RECEIVER_PORT}")

            while True:
                positions = get_servo_positions(tuna)
                client_socket.sendall(str(positions).encode('utf-8'))
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping controller...")
    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
