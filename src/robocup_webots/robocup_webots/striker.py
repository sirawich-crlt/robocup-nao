"""Striker: find the ball and walk to it."""
import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from std_msgs.msg import String

CENTRE = 0.3
NEAR = 0.04


class Striker(Node):
    def __init__(self):
        super().__init__('striker')

        self.robot = self.declare_parameter('robot', 'red_striker').value
        self.get_logger().info(f'Striker started for {self.robot}')

        self.ball = None
        self.create_subscription(Point, f'/{self.robot}/ball', self.on_ball, 1)
        self.cmd = self.create_publisher(String, f'/{self.robot}/cmd', 1)
        self.create_timer(0.5, self.decide)

    def on_ball(self, msg):
        self.ball = msg

    def decide(self):
        if self.ball is None:
            return

        if self.ball.z == 0.0:
            state, action = 'SEARCH', 'left'
        elif self.ball.y > NEAR:
            state, action = 'REACHED', None
        elif self.ball.x < -CENTRE:
            state, action = 'TURN', 'left'
        elif self.ball.x > CENTRE:
            state, action = 'TURN', 'right'
        else:
            state, action = 'APPROACH', 'walk'

        self.get_logger().info(f'{state}  x={self.ball.x:.2f}  size={self.ball.y:.4f}',
                               throttle_duration_sec=1.0)
        if action:
            self.cmd.publish(String(data=action))


def main():
    rclpy.init()
    node = Striker()
    rclpy.spin(node)


if __name__ == '__main__':
    main()