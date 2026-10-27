"""Goalkeeper."""
import rclpy
from rclpy.node import Node


class Goalkeeper(Node):
    def __init__(self):
        super().__init__('goalkeeper')

        # Which robot this is (given by the launch file): red_goalkeeper or blue_goalkeeper
        self.robot = self.declare_parameter('robot', 'red_goalkeeper').value
        self.get_logger().info(f'Goalkeeper started for {self.robot}')

        # Write your code here


def main():
    rclpy.init()
    node = Goalkeeper()
    rclpy.spin(node)


if __name__ == '__main__':
    main()