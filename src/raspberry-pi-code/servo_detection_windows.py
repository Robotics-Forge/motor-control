import os
import sys

# Dynamically add the feetech-tuna directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_tuna_path = os.path.abspath(os.path.join(current_dir, '..', 'feetech-tuna'))
sys.path.append(feetech_tuna_path)

import serial.tools.list_ports
from feetech_tuna import FeetechTuna


def list_serial_ports():
    """List all available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def detect_servos(port, baudrate=1000000):
    """
    Detect servos connected to the given port.
    Returns a list of detected servo IDs.
    """
    detected_servos = []
    tuna = FeetechTuna()

    if not tuna.openSerialPort(port=port, baudrate=baudrate):
        print(f"Failed to open port {port}")
        return detected_servos

    print(f"Scanning for servos on {port}...")
    try:
        for servo_id in range(1, 51):  # Scan only up to servo ID 50
            position = tuna.readReg(servo_id, 56)  # Read position register
            if position is not None:
                detected_servos.append(servo_id)
                print(f"Detected servo ID: {servo_id}, Position: {position}")
    except Exception as e:
        print(f"Error scanning port {port}: {e}")
    finally:
        tuna.closeSerialPort()

    return detected_servos

def main():
    print("Scanning all available COM ports...")
    available_ports = list_serial_ports()

    if not available_ports:
        print("No available COM ports detected.")
        return

    print("Available COM ports:")
    for idx, port in enumerate(available_ports):
        print(f"[{idx + 1}] {port}")

    try:
        selection = int(input("\nSelect a COM port by entering its number: ")) - 1
        if selection < 0 or selection >= len(available_ports):
            print("Invalid selection. Exiting.")
            return

        selected_port = available_ports[selection]
        print(f"\nChecking {selected_port}...")
        servos = detect_servos(selected_port)
        if servos:
            print(f"Motors detected on {selected_port}: {servos}")
        else:
            print(f"No motors found on {selected_port}.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()

