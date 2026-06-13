#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    camera_node = Node(
        package="camera_ros",
        executable="camera_node",
        name="camera",
        output="screen",
        parameters=[
            {
                "width": 640,
                "height": 480,
                "role": "video",
                "format": "BGR888",
                "frame_id": "camera_optical_frame",
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }
        ],
        remappings=[
            ("~/image_raw", "/camera/image_raw"),
            ("~/camera_info", "/camera/camera_info"),
        ],
    )

    ball_localizer_node = Node(
        package="pavlov_controller",
        executable="ball_localizer.py",
        name="ball_localizer",
        output="screen",
        parameters=[
            {"use_sim_time": LaunchConfiguration("use_sim_time")},
            {"image_topic": LaunchConfiguration("image_topic")},
            {"camera_info_topic": LaunchConfiguration("camera_info_topic")},
            {"output_frame": LaunchConfiguration("output_frame")},
            {"camera_frame_id": LaunchConfiguration("camera_frame_id")},
            {"camera_info_fallback": LaunchConfiguration("camera_info_fallback")},
            {"camera_pitch_rad": LaunchConfiguration("camera_pitch_rad")},
            {"ball_radius_m": LaunchConfiguration("ball_radius_m")},
            {"min_radius_px": LaunchConfiguration("min_radius_px")},
            {"max_range_m": LaunchConfiguration("max_range_m")},
            {"kernel_size": LaunchConfiguration("kernel_size")},
            {"sat_min": LaunchConfiguration("sat_min")},
            {"val_min": LaunchConfiguration("val_min")},
            {"publish_debug_image": LaunchConfiguration("publish_debug_image")},
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),

            DeclareLaunchArgument(
                "image_topic",
                default_value="/camera/image_raw"
            ),

            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/camera/camera_info"
            ),

            DeclareLaunchArgument(
                "output_frame",
                default_value="base_link"
            ),

            DeclareLaunchArgument(
                "camera_frame_id",
                default_value="camera_optical_frame"
            ),

            DeclareLaunchArgument(
                "camera_info_fallback",
                default_value="true"
            ),

            DeclareLaunchArgument(
                "camera_pitch_rad",
                default_value="0.0"
            ),

            DeclareLaunchArgument(
                "ball_radius_m",
                default_value="0.0335"
            ),

            DeclareLaunchArgument(
                "min_radius_px",
                default_value="3.0"
            ),

            DeclareLaunchArgument(
                "max_range_m",
                default_value="6.0"
            ),

            DeclareLaunchArgument(
                "kernel_size",
                default_value="5"
            ),

            DeclareLaunchArgument(
                "sat_min",
                default_value="120"
            ),

            DeclareLaunchArgument(
                "val_min",
                default_value="80"
            ),

            DeclareLaunchArgument(
                "publish_debug_image",
                default_value="true"
            ),

            camera_node,
            ball_localizer_node,
        ]
    )