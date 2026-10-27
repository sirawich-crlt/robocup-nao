import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from controller import Motion
from sensor_msgs.msg import Image
from std_msgs.msg import String

MOVES = {
    'walk': 'Forwards.motion',
    'left': 'TurnLeft40.motion',
    'right': 'TurnRight40.motion',
}


class NaoDriver:
    def init(self, webots_node, properties):
        self.robot = webots_node.robot
        name = self.robot.getName()

        # Moves
        folder = os.path.join(get_package_share_directory('robocup_webots'), 'motions')
        self.moves = {cmd: Motion(os.path.join(folder, f)) for cmd, f in MOVES.items()}
        self.current = None

        # ROS 2: commands for this robot on /<robot>/cmd
        rclpy.init(args=None)
        self.node = rclpy.create_node(f'{name}_driver')
        self.node.create_subscription(String, f'/{name}/cmd', self.on_cmd, 1)

        self.robot.getDevice('HeadPitch').setPosition(0.3)
        self.robot.getDevice('LShoulderPitch').setPosition(1.5)
        self.robot.getDevice('RShoulderPitch').setPosition(1.5)

        self.camera = self.robot.getDevice('CameraTop')
        self.camera.enable(100)
        self.image_pub = self.node.create_publisher(Image, f'/{name}/camera/image_color', 1)
        self.last_image = 0.0

    def on_cmd(self, msg):
        if self.current and not self.current.isOver():
            return
        move = self.moves.get(msg.data)
        if move:
            move.setTime(0)
            move.play()
            self.current = move

    def step(self):
        rclpy.spin_once(self.node, timeout_sec=0)

        now = self.robot.getTime()
        if now - self.last_image >= 0.1:
            self.last_image = now
            data = self.camera.getImage()
            if data:
                img = Image()
                img.width = self.camera.getWidth()
                img.height = self.camera.getHeight()
                img.encoding = 'bgra8'
                img.step = img.width * 4
                img.data = data
                self.image_pub.publish(img)