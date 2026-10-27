"""Defender."""
import rclpy
from rclpy.node import Node


class Defender(Node):
    def __init__(self):
        super().__init__('defender')

        # Which robot this is (given by the launch file):
        # red_defender_1, red_defender_2, blue_defender_1 or blue_defender_2
        self.robot = self.declare_parameter('robot', 'red_defender_1').value
        self.get_logger().info(f'Defender started for {self.robot}')

        # Write your code here


def main():
    rclpy.init()
    node = Defender()
    rclpy.spin(node)


if __name__ == '__main__':
    main()