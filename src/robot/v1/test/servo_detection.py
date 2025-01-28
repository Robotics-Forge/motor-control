import serial.tools.list_ports
from motor_control import MotorController

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
    controller = MotorController()

    if not controller.connect(port=port, baudrate=baudrate):
        print(f"Failed to open port {port}")
        return detected_servos

    print(f"Scanning for servos on {port}...")
    try:
        # Get all possible servo IDs from the motor controller
        servo_ids = controller.get_ids()

        # Get positions for all servos at once
        positions = controller.get_positions(servo_ids)

        # Check which servos returned valid positions
        for servo_id, position in zip(servo_ids, positions):
            if position is not None:
                detected_servos.append(servo_id)
                print(f"Detected servo ID: {servo_id}, Position: {position}")
    except Exception as e:
        print(f"Error scanning port {port}: {e}")
    finally:
        controller.disconnect()

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

