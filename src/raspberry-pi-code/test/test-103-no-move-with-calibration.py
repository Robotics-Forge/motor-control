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
SMS_STS_GOAL_POSITION_L = 42
SMS_STS_GOAL_POSITION_H = 43
SMS_STS_MOVING = 66

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

        # Read initial position and offset
        current_pos = tuna.readReg(SERVO_ID, SMS_STS_PRESENT_POSITION_L)
        current_offset = tuna.readReg(SERVO_ID, SMS_STS_OFS_L)
        print(f"Initial position: {current_pos}")
        print(f"Current offset: {current_offset}")

        # Set offset
        tuna.writeReg(SERVO_ID, SMS_STS_LOCK, 0)  # unlock EPROM
        time.sleep(0.1)

        offset = 991
        print(f"\nSetting offset to {offset}...")
        tuna.writeReg(SERVO_ID, SMS_STS_OFS_L, offset)  # Low byte
        time.sleep(0.1)

        new_offset = tuna.readReg(SERVO_ID, SMS_STS_OFS_L)
        print(f"New offset: {new_offset}")

        tuna.writeReg(SERVO_ID, SMS_STS_LOCK, 1)  # lock EPROM
        time.sleep(0.1)

        # Read position after offset
        current_pos = tuna.readReg(SERVO_ID, SMS_STS_PRESENT_POSITION_L)
        print(f"Position after setting offset: {current_pos}")

        # Move to position
        # position = 4000
        # print(f"\nMoving to position {position}...")
        # tuna.writeReg(SERVO_ID, SMS_STS_GOAL_POSITION_L, position)  # Low byte

        # Wait for movement to complete
        # while True:
        #     time.sleep(0.1)
        #     moving = tuna.readReg(SERVO_ID, SMS_STS_MOVING)
        #     if not moving:
        #         break

        # Read final position
        final_pos = tuna.readReg(SERVO_ID, SMS_STS_PRESENT_POSITION_L)
        print()
        print(f"Final position: {final_pos}")
        print(f"Final offset: {new_offset}")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    finally:
        tuna.closeSerialPort()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
