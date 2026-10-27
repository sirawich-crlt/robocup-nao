import numpy as np
import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from sensor_msgs.msg import Image


class BallDetector(Node):
    def __init__(self):
        super().__init__('ball_detector')
        robot = self.declare_parameter('robot', 'red_striker').value
        self.create_subscription(Image, f'/{robot}/camera/image_color', self.on_image, 1)
        self.pub = self.create_publisher(Point, f'/{robot}/ball', 1)

    def on_image(self, msg):
        channels = msg.step // msg.width
        img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, channels)
        b = img[:, :, 0].astype(int)
        g = img[:, :, 1].astype(int)
        r = img[:, :, 2].astype(int)

        # Orange
        orange = (r > 150) & (g > 50) & (g < 170) & (b < 90)
        ys, xs = np.nonzero(orange)

        ball = Point()
        if len(xs) > 5:
            ball.x = (xs.mean() - msg.width / 2) / (msg.width / 2)
            ball.y = len(xs) / (msg.width * msg.height)
            ball.z = 1.0
            side = 'LEFT' if ball.x < -0.3 else 'RIGHT' if ball.x > 0.3 else 'CENTRE'
            self.get_logger().info(f'BALL SEEN: {side}  x={ball.x:.2f}  size={ball.y:.4f}',
                                   throttle_duration_sec=1.0)
        else:
            ball.z = 0.0
            self.get_logger().info('no ball', throttle_duration_sec=1.0)
        self.pub.publish(ball)


def main():
    rclpy.init()
    rclpy.spin(BallDetector())


if __name__ == '__main__':
    main()