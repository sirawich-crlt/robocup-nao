"""Striker: find the ball, walk to it and kick."""
import rclpy
from geometry_msgs.msg import Point
from rclpy.node import Node
from std_msgs.msg import String

CENTRE = 0.4
NEAR = 0.05        
FAR = 0.01        
SEARCH_PLAN = ['left'] + ['right'] * 2 + ['left'] * 9
BLOCKING = {'left': 3.0, 'right': 3.0, 'kick': 5.0, 'back': 2.7}


class Striker(Node):
    def __init__(self):
        super().__init__('striker')

        self.robot = self.declare_parameter('robot', 'red_striker').value
        self.ball = None
        self.was_close = False
        self.search_step = 0
        self.busy_until = 0.0
        self.head = None
        self.create_subscription(Point, f'/{self.robot}/ball', self.on_ball, 1)
        self.cmd = self.create_publisher(String, f'/{self.robot}/cmd', 1)
        self.create_timer(0.5, self.decide)

    def on_ball(self, msg):
        self.ball = msg

    def now(self):
        return self.get_clock().now().nanoseconds / 1e9

    def decide(self):
        if self.ball is None or self.now() < self.busy_until:
            return

        if self.ball.z == 0.0:
            if self.was_close:
                state, action = 'BACK', 'back'
                self.was_close = False
            else:
                action = SEARCH_PLAN[self.search_step % len(SEARCH_PLAN)]
                state = f'SEARCH {self.search_step % len(SEARCH_PLAN) + 1}/{len(SEARCH_PLAN)}'
                self.search_step += 1
        elif self.ball.y >= 1.0:
            state, action = 'KICK', 'kick'
        elif self.ball.x < -CENTRE:
            if self.ball.y > FAR:
                state, action = 'TURN (small)', 'small_left'
            else:
                state, action = 'TURN', 'left'
        elif self.ball.x > CENTRE:
            if self.ball.y > FAR:
                state, action = 'TURN (small)', 'small_right'
            else:
                state, action = 'TURN', 'right'
        elif self.ball.y >= NEAR:
            state, action = 'CLOSE', 'small_step'
        elif self.ball.y < FAR:
            state, action = 'APPROACH (far)', 'walk_long'
        else:
            state, action = 'APPROACH', 'walk'

        if self.ball.z == 1.0:
            self.was_close = self.ball.y >= NEAR
            self.search_step = 0

        want = None
        if self.ball.z == 1.0 and self.ball.y > FAR:
            want = 'head_down'
        elif self.ball.z == 0.0 and not self.was_close:
            want = 'head_up'
        if want and want != self.head:
            self.cmd.publish(String(data=want))
            self.head = want

        self.get_logger().info(f'{state}  x={self.ball.x:.2f}  size={self.ball.y:.4f}',
                               throttle_duration_sec=1.0)
        self.cmd.publish(String(data=action))
        if action in BLOCKING:
            self.busy_until = self.now() + BLOCKING[action]


def main():
    rclpy.init()
    node = Striker()
    rclpy.spin(node)


if __name__ == '__main__':
    main()