#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_external_odom = LaunchConfiguration("use_external_odom")
    goal_topic = LaunchConfiguration("goal_topic")

    max_linear_speed = LaunchConfiguration("max_linear_speed")
    max_angular_speed = LaunchConfiguration("max_angular_speed")

    go_to_goal = Node(
        package="pavlov_controller",
        executable="go_to_goal.py",
        name="go_to_goal",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"use_external_odom": use_external_odom},
            {"goal_topic": goal_topic},
            {"cmd_vel_topic": "/cmd_vel"},
            {"max_linear_speed": max_linear_speed},
            {"max_angular_speed": max_angular_speed},
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation time",
            ),
            DeclareLaunchArgument(
                "use_external_odom",
                default_value="false",
                description="true: use /odom, false: internal integration",
            ),
            DeclareLaunchArgument(
                "goal_topic",
                default_value="/goal_pose",
                description="Topic for PoseStamped goal messages",
            ),
            DeclareLaunchArgument(
                "max_linear_speed",
                default_value="0.10",
                description="go_to_goal max linear speed (m/s)",
            ),
            DeclareLaunchArgument(
                "max_angular_speed",
                default_value="1.2",
                description="go_to_goal max angular speed (rad/s)",
            ),
            go_to_goal,
        ]
    )