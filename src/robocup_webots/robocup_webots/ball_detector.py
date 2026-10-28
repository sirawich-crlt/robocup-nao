import numpy as np
import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from sensor_msgs.msg import Image

BOTTOM_TOPIC = 'CameraBottom'  
KICK_SIZE = 0.13

def find_ball(msg):
    """Return (x, size, v) of the orange ball, or None.
    x: -1 left .. +1 right, size: fraction of image, v: 0 top .. 1 bottom of image."""
    channels = msg.step // msg.width
    img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, channels)
    b = img[:, :, 0].astype(int)
    g = img[:, :, 1].astype(int)
    r = img[:, :, 2].astype(int)

    # Orange: strong red, green about 35-75% of red, little blue
    # (red robot parts have very little green, so they are ignored)
    orange = (r > 150) & (g > 0.35 * r) & (g < 0.75 * r) & (b < 0.45 * r)
    ys, xs = np.nonzero(orange)
    if len(xs) <= 5:
        return None
    x = (xs.mean() - msg.width / 2) / (msg.width / 2)
    size = len(xs) / (msg.width * msg.height)
    v = ys.mean() / msg.height
    return x, size, v


class BallDetector(Node):
    def __init__(self):
        super().__init__('ball_detector')
        robot = self.declare_parameter('robot', 'red_striker').value
        self.bottom = None
        self.create_subscription(Image, f'/{robot}/camera/image_color', self.on_top, 1)
        self.create_subscription(Image, f'/{robot}/{BOTTOM_TOPIC}/image_color', self.on_bottom, 1)
        self.pub = self.create_publisher(Point, f'/{robot}/ball', 1)

    def on_bottom(self, msg):
        self.bottom = find_ball(msg)

    def on_top(self, msg):
        top = find_ball(msg)
        ball = Point()
        if top:
            ball.x, ball.y = top[0], top[1]
            ball.z = 1.0
            where = 'TOP'
        elif self.bottom:
            x, size, v = self.bottom
            ball.x = x
            ball.z = 1.0
            if size > KICK_SIZE:
                ball.y = 1.0          # ball fills the bottom camera = kick now
                where = f'BOTTOM (kick) bottom_size={size:.2f}'
            else:
                ball.y = 0.05         # seen below, but keep walking
                where = f'BOTTOM (near) bottom_size={size:.2f}'
        else:
            ball.z = 0.0
            where = None

        if where:
            self.get_logger().info(f'BALL SEEN [{where}] x={ball.x:.2f} size={ball.y:.4f}',
                                   throttle_duration_sec=1.0)
        else:
            self.get_logger().info('no ball', throttle_duration_sec=1.0)
        self.pub.publish(ball)


def main():
    rclpy.init()
    rclpy.spin(BallDetector())


if __name__ == '__main__':
    main()