import rclpy
from rclpy.node import Node
from gpiozero import Servo
from std_msgs.msg import Float64

class ServoControlNode(Node):
    def __init__(self):
        super().__init__('servo_control_node')

        # Initialize the 270-degree servo on GPIO pin 18
        self.servo = Servo(18)

        # Create a timer to move the servo at intervals
        self.timer = self.create_timer(3.0, self.move_servo)  # Move the servo every 3 seconds

        # Track the state of the servo for printing the angle
        self.moving_forward = True  # Flag to determine if we are moving to max or min

    def move_servo(self):
        if self.moving_forward:
            self.servo.value = 1.5  # Move to max position (typically 270° for a 270° servo)
            self.get_logger().info(f'Servo Angle: 270°')  # Print max angle (270°)
        else:
            self.servo.value = -1.5  # Move to min position (typically 0° for a 270° servo)
            self.get_logger().info(f'Servo Angle: 0°')  # Print min angle (0°)
        
        # Toggle the direction for the next move
        self.moving_forward = not self.moving_forward

def main(args=None):
    rclpy.init(args=args)
    node = ServoControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
