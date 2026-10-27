import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher

# robot name in pitch.wbt -> role program
ROBOTS = {
    'red_goalkeeper': 'goalkeeper',
    'red_defender_1': 'defender',
    'red_defender_2': 'defender',
    'red_striker': 'striker',
    'blue_goalkeeper': 'goalkeeper',
    'blue_defender_1': 'defender',
    'blue_defender_2': 'defender',
    'blue_striker': 'striker',
}


def generate_launch_description():
    pkg = get_package_share_directory('robocup_webots')
    urdf = os.path.join(pkg, 'resource', 'nao.urdf')

    webots = WebotsLauncher(world=os.path.join(pkg, 'worlds', 'pitch.wbt'))
    actions = [webots]

    for robot, role in ROBOTS.items():
        # Body (driver inside Webots)
        actions.append(WebotsController(
            robot_name=robot,
            parameters=[{'robot_description': urdf}],
        ))
        # Eyes (ball detector)
        actions.append(Node(
            package='robocup_webots',
            executable='ball_detector',
            name=f'{robot}_ball_detector',
            parameters=[{'robot': robot}],
        ))
        # Brain (striker / defender / goalkeeper)
        actions.append(Node(
            package='robocup_webots',
            executable=role,
            name=f'{robot}_brain',
            parameters=[{'robot': robot}],
            output='screen',
        ))

    # When Webots closes, stop everything
    actions.append(launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=webots,
            on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
        )
    ))

    return LaunchDescription(actions)