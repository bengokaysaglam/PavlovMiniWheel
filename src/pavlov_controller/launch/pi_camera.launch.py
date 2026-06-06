#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("device", default_value="/dev/video0", description="Video device for Pi Camera")
        , DeclareLaunchArgument("image_topic", default_value="/camera/image_raw", description="Camera image topic")
        , DeclareLaunchArgument("camera_info_topic", default_value="/camera/camera_info", description="Camera info topic")
        , DeclareLaunchArgument("camera_frame_id", default_value="camera_link", description="Camera frame id")
        , DeclareLaunchArgument("image_width", default_value="640", description="Image width")
        , DeclareLaunchArgument("image_height", default_value="480", description="Image height")
        , DeclareLaunchArgument("frame_rate", default_value="30.0", description="Camera frame rate")
        , DeclareLaunchArgument("fx", default_value="530.47", description="Camera intrinsic fx")
        , DeclareLaunchArgument("fy", default_value="529.08", description="Camera intrinsic fy")
        , DeclareLaunchArgument("cx", default_value="320.0", description="Camera intrinsic cx")
        , DeclareLaunchArgument("cy", default_value="240.0", description="Camera intrinsic cy")
        , DeclareLaunchArgument("distortion_model", default_value="plumb_bob", description="Camera distortion model")
        , DeclareLaunchArgument("distortion_coefficients", default_value="[0.0,0.0,0.0,0.0,0.0]", description="Camera distortion coefficients")
        , DeclareLaunchArgument("capture_backend", default_value="v4l2", description="OpenCV capture backend")

        , Node(
            package="pavlov_controller",
            executable="pi_camera_node.py",
            name="pi_camera_node",
            output="screen",
            parameters=[
                {"device": LaunchConfiguration("device")},
                {"image_topic": LaunchConfiguration("image_topic")},
                {"camera_info_topic": LaunchConfiguration("camera_info_topic")},
                {"camera_frame_id": LaunchConfiguration("camera_frame_id")},
                {"image_width": LaunchConfiguration("image_width")},
                {"image_height": LaunchConfiguration("image_height")},
                {"frame_rate": LaunchConfiguration("frame_rate")},
                {"fx": LaunchConfiguration("fx")},
                {"fy": LaunchConfiguration("fy")},
                {"cx": LaunchConfiguration("cx")},
                {"cy": LaunchConfiguration("cy")},
                {"distortion_model": LaunchConfiguration("distortion_model")},
                {"distortion_coefficients": LaunchConfiguration("distortion_coefficients")},
                {"capture_backend": LaunchConfiguration("capture_backend")},
            ],
        ),
    ])
