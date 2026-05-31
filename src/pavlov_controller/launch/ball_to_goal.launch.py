from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("ball_point_topic", default_value="/ball/point"),
            DeclareLaunchArgument("ball_visible_topic", default_value="/ball/visible"),
            DeclareLaunchArgument("goal_topic", default_value="/goal_pose"),
            DeclareLaunchArgument("publish_rate_hz", default_value="5.0"),
            DeclareLaunchArgument("visible_timeout_sec", default_value="0.6"),
            DeclareLaunchArgument("standoff_m", default_value="0.25"),
            DeclareLaunchArgument("min_ball_x_m", default_value="0.15"),
            DeclareLaunchArgument("goal_frame", default_value="base_link"),

            Node(
                package="pavlov_controller",
                executable="ball_to_goal.py",
                name="ball_to_goal",
                output="screen",
                parameters=[
                    {"use_sim_time": LaunchConfiguration("use_sim_time")},
                    {"ball_point_topic": LaunchConfiguration("ball_point_topic")},
                    {"ball_visible_topic": LaunchConfiguration("ball_visible_topic")},
                    {"goal_topic": LaunchConfiguration("goal_topic")},
                    {"publish_rate_hz": LaunchConfiguration("publish_rate_hz")},
                    {"visible_timeout_sec": LaunchConfiguration("visible_timeout_sec")},
                    {"standoff_m": LaunchConfiguration("standoff_m")},
                    {"min_ball_x_m": LaunchConfiguration("min_ball_x_m")},
                    {"goal_frame": LaunchConfiguration("goal_frame")},
                ],
            ),
        ]
    )