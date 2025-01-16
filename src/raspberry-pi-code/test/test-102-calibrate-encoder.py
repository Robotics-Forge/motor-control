import os
import sys
import time

# Add the feetech-tuna directory dynamically to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
feetech_tuna_path = os.path.abspath(os.path.join(current_dir, '../..', 'feetech-tuna'))
sys.path.append(feetech_tuna_path)
from feetech_tuna import FeetechTuna
import serial.tools.list_ports

SERVO_ID = 1
SMS_STS_TORQUE_ENABLE = 40
SMS_STS_OFS_L = 31
SMS_STS_OFS_H = 32
SMS_STS_LOCK = 55
SMS_STS_PRESENT_POSITION_L = 56
SMS_STS_PRESENT_POSITION_H = 57

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

        # Disable torque first
        print("Disabling torque...")
        tuna.writeReg(SERVO_ID, SMS_STS_TORQUE_ENABLE, 0)
        time.sleep(0.1)

        # Read current position
        current_pos = tuna.readReg(SERVO_ID, SMS_STS_PRESENT_POSITION_L)
        print(f"Current position before offset: {current_pos}")

        # Unlock EPROM to allow writing to offset registers
        tuna.writeReg(SERVO_ID, SMS_STS_LOCK, 0)  # unlock
        time.sleep(0.1)

        # Write the negative of current position as offset
        # This will make the current position read as 0
        #offset = -current_pos & 0xFF  # Keep within byte range
        offset = 1000
        print()
        print(f"Setting offset to: {offset}")
        print()
        tuna.writeReg(SERVO_ID, SMS_STS_OFS_L, offset)
        time.sleep(0.1)

        # Lock EPROM to protect the offset value
        tuna.writeReg(SERVO_ID, SMS_STS_LOCK, 1)  # lock
        time.sleep(0.1)

        # Verify new position
        new_pos = tuna.readReg(SERVO_ID, SMS_STS_PRESENT_POSITION_L)
        print(f"Position after offset: {new_pos}")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    finally:
        tuna.closeSerialPort()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
