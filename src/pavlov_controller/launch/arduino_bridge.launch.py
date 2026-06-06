from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration("use_sim_time")

    node = Node(
        package="pavlov_controller",
        executable="arduino_serial_bridge.py",
        name="arduino_serial_bridge",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "serial_port": LaunchConfiguration("serial_port"),
                "baud_rate": LaunchConfiguration("baud_rate"),
                "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
                "wheel_radius": LaunchConfiguration("wheel_radius"),
                "wheel_separation": LaunchConfiguration("wheel_separation"),
                "command_prefix": LaunchConfiguration("command_prefix"),
                "max_wheel_speed": LaunchConfiguration("max_wheel_speed"),
                "reconnect_interval": LaunchConfiguration("reconnect_interval"),
            }
        ],
    )

    return [node]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulation time",
        ),
        DeclareLaunchArgument(
            "serial_port",
            default_value="/dev/ttyACM0",
            description="Arduino serial port",
        ),
        DeclareLaunchArgument(
            "baud_rate",
            default_value="115200",
            description="Arduino serial baud rate",
        ),
        DeclareLaunchArgument(
            "cmd_vel_topic",
            default_value="/cmd_vel",
            description="Twist topic to subscribe for mobile base commands",
        ),
        DeclareLaunchArgument(
            "wheel_radius",
            default_value="0.0325",
            description="Wheel radius in meters",
        ),
        DeclareLaunchArgument(
            "wheel_separation",
            default_value="0.1071",
            description="Distance between left and right wheels",
        ),
        DeclareLaunchArgument(
            "command_prefix",
            default_value="V",
            description="Serial command prefix for Arduino parsing",
        ),
        DeclareLaunchArgument(
            "max_wheel_speed",
            default_value="40.0",
            description="Maximum wheel angular velocity in rad/s",
        ),
        DeclareLaunchArgument(
            "reconnect_interval",
            default_value="1.0",
            description="Seconds between serial reconnect attempts",
        ),
        OpaqueFunction(function=launch_setup),
    ])
