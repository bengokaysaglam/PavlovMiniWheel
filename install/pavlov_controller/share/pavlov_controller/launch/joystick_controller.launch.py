import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Joystick Node
    joystick_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[{
            'device_id': 0,
            'deadzone': 0.05,
            'autorepeat_rate': 20.0,
        }]
    )

    # Joystick Controller Node
    controller_node = Node(
        package='pavlov_controller',
        executable='joystick_controller.py',
        name='joystick_controller',
        output='screen'
    )

    return LaunchDescription([
        joystick_node,
        controller_node,
    ])