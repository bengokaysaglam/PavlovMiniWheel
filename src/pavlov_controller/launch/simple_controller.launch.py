from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")

    wheel_radius = float(LaunchConfiguration("wheel_radius").perform(context))
    wheel_separation = float(LaunchConfiguration("wheel_separation").perform(context))

    wheel_radius_error = float(LaunchConfiguration("wheel_radius_error").perform(context))
    wheel_separation_error = float(LaunchConfiguration("wheel_separation_error").perform(context))

    simple_controller_node = Node(
        package="pavlov_controller",
        executable="simple_controller.py",
        name="simple_controller",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "wheel_radius": wheel_radius + wheel_radius_error,
                "wheel_separation": wheel_separation + wheel_separation_error,
            }
        ],
    )

    return [simple_controller_node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time"
        ),

        DeclareLaunchArgument(
            "wheel_radius",
            default_value="0.0325",
            description="Wheel radius in meters"
        ),

        DeclareLaunchArgument(
            "wheel_separation",
            default_value="0.1071",
            description="Distance between left and right wheels"
        ),

        DeclareLaunchArgument(
            "wheel_radius_error",
            default_value="0.0",
            description="Wheel radius correction"
        ),

        DeclareLaunchArgument(
            "wheel_separation_error",
            default_value="0.0",
            description="Wheel separation correction"
        ),

        OpaqueFunction(function=launch_setup),
    ])