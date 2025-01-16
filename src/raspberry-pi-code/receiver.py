import socket
import serial.tools.list_ports
from motor_util import initialize_servos, SERVO_PAIRS
from feetech_tuna import FeetechTuna

# Network configuration
HOST = '192.168.1.171'
PORT = 12345

# Multiplier system
MULTIPLIER_MAP = {
    # Motors with 5x multiplier
    24: 4, 25: 4, 26: 4, 27: 4,
    34: 4, 35: 4, 36: 4, 37: 4,
}

DEFAULT_MULTIPLIER = 1  # Default multiplier for all other motors

# Motors to reverse direction (ONLY 4 series and 7 series)
REVERSED_MOTORS = {24, 34, 26, 36}

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

    tuna = FeetechTuna()
    try:
        # Open serial port
        if not tuna.openSerialPort(port=selected_port, baudrate=1000000):
            print(f"Failed to open serial port {selected_port}.")
            return

        # Initialize servos
        initialize_servos(tuna)

        print("\nRetrieving initial positions for slave servos...")
        # Retrieve current positions of slave servos as their baseline
        slave_baselines = {
            follower_id: tuna.readReg(follower_id, 56) or 2048 for _, follower_id in SERVO_PAIRS
        }
        print(f"Initial Slave Baselines: {slave_baselines}")

        # Placeholder for master servo baselines
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
                    # Parse received master positions
                    commands = eval(data)  # Replace with `json.loads` if using JSON
                    print(f"Received master positions: {commands}")

                    # Initialize master baselines on the first command received
                    if master_baselines is None:
                        master_baselines = commands.copy()
                        print(f"Master baselines initialized: {master_baselines}")

                    # Update slave servos based on deltas
                    for master_id, master_new_position in commands.items():
                        # Find corresponding slave servo
                        slave_id = next(
                            (pair[1] for pair in SERVO_PAIRS if pair[0] == master_id), None
                        )
                        if slave_id is None:
                            print(f"No slave servo mapped to Master {master_id}, skipping...")
                            continue

                        # Calculate delta for the master servo with wraparound handling
                        range_max = 4096  # Max value for servo position
                        half_range = range_max // 2

                        # Raw delta
                        master_delta = master_new_position - master_baselines[master_id]

                        # Adjust for wraparound
                        if master_delta > half_range:
                            master_delta -= range_max
                        elif master_delta < -half_range:
                            master_delta += range_max

                        # Reverse delta for specific motors (4 and 7 series only)
                        if slave_id in REVERSED_MOTORS:
                            master_delta *= -1

                        # Apply multiplier
                        multiplier = MULTIPLIER_MAP.get(slave_id, DEFAULT_MULTIPLIER)
                        scaled_delta = master_delta * multiplier

                        # Calculate new position for the slave servo
                        slave_new_position = slave_baselines[slave_id] + scaled_delta
                        slave_new_position = max(0, min(4095, slave_new_position))  # Clamp to valid range

                        # Move the slave servo
                        success = tuna.writeReg(slave_id, 42, int(slave_new_position))
                        if success:
                            print(
                                f"Master {master_id} moved to {master_new_position} (Delta: {master_delta}, Scaled Delta: {scaled_delta}). "
                                f"Slave {slave_id} set to {slave_new_position}."
                            )
                        else:
                            print(f"Failed to move Slave {slave_id} to {slave_new_position}.")

                        # Update Hand Position

                except Exception as e:
                    print(f"Error processing commands: {e}")
    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        tuna.closeSerialPort()

if __name__ == "__main__":
    main()
