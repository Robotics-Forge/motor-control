# Robot Teleoperation Control System

This repository contains the teleoperation motor control system for a robot, allowing remote control capabilities.

## System Overview

The system consists of two main components:

-   A receiver program that runs on the robot
-   A controller program that runs on the control device (e.g., computer, remote control)

## Setup Instructions

### On the Robot

1. Navigate to the project directory
2. Run the receiver program:
    ```bash
    python receiver.py
    ```

### On the Control Device

1. Navigate to the project directory
2. Run the controller program:
    ```bash
    python controller.py
    ```

## Important Notes

-   Ensure both devices are connected to the same network
-   The receiver must be running on the robot before starting the controller
-   Check all connections and power before operating

## Requirements

-   Python 3.x

## Troubleshooting

If you experience connection issues:

1. Verify both devices are on the same network
2. Check that no firewalls are blocking the connection
3. Ensure the receiver program is running before the controller
4. Ensure the servo driver has power and the servos are connected

## License

(Add your license information here)
