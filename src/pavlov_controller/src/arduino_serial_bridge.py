#!/usr/bin/env python3

import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

try:
    import serial
    from serial import SerialException
except ImportError:
    serial = None
    SerialException = Exception

class ArduinoSerialBridge(Node):
    def __init__(self):
        super().__init__("arduino_serial_bridge")

        self.declare_parameter("serial_port", "/dev/ttyACM0")
        self.declare_parameter("baud_rate", 115200)
        self.declare_parameter("serial_timeout", 0.1)
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("wheel_radius", 0.0325)
        self.declare_parameter("wheel_separation", 0.1071)
        self.declare_parameter("command_prefix", "V")
        self.declare_parameter("max_wheel_speed", 40.0)
        self.declare_parameter("reconnect_interval", 1.0)

        self.serial_port = self.get_parameter("serial_port").value
        self.baud_rate = self.get_parameter("baud_rate").value
        self.serial_timeout = self.get_parameter("serial_timeout").value
        self.cmd_vel_topic = self.get_parameter("cmd_vel_topic").value
        self.wheel_radius = self.get_parameter("wheel_radius").value
        self.wheel_separation = self.get_parameter("wheel_separation").value
        self.command_prefix = self.get_parameter("command_prefix").value
        self.max_wheel_speed = self.get_parameter("max_wheel_speed").value
        self.reconnect_interval = self.get_parameter("reconnect_interval").value

        self.ser = None
        self.last_connect_time = 0.0

        self.get_logger().info(f"ArduinoSerialBridge started; port={self.serial_port} baud={self.baud_rate}")

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self.cmd_vel_callback,
            10,
        )

        self.serial_timer = self.create_timer(self.reconnect_interval, self.ensure_serial)
        self.ensure_serial()

    def compute_wheel_speeds(self, linear_velocity: float, angular_velocity: float):
        left = (linear_velocity - (angular_velocity * self.wheel_separation / 2.0)) / self.wheel_radius
        right = (linear_velocity + (angular_velocity * self.wheel_separation / 2.0)) / self.wheel_radius
        left = max(min(left, self.max_wheel_speed), -self.max_wheel_speed)
        right = max(min(right, self.max_wheel_speed), -self.max_wheel_speed)
        return left, right

    def cmd_vel_callback(self, msg: Twist):
        left_speed, right_speed = self.compute_wheel_speeds(msg.linear.x, msg.angular.z)
        self.send_wheel_command(left_speed, right_speed)

    def ensure_serial(self):
        now = time.time()
        if self.ser is not None and self.ser.is_open:
            return

        if now - self.last_connect_time < self.reconnect_interval:
            return

        self.last_connect_time = now

        if serial is None:
            self.get_logger().error(
                "pyserial is not installed. Install python3-serial or pip install pyserial."
            )
            return

        try:
            self.get_logger().info(f"Opening serial port {self.serial_port}...")
            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=self.serial_timeout,
            )
            self.get_logger().info(f"Serial port opened: {self.serial_port}")
        except SerialException as exc:
            self.get_logger().warn(f"Cannot open serial port {self.serial_port}: {exc}")
            self.ser = None

    def send_wheel_command(self, left_speed: float, right_speed: float):
        if self.ser is None or not self.ser.is_open:
            self.get_logger().warn(
                "Serial port not available; cannot send wheel command."
            )
            return

        command = f"{self.command_prefix},{left_speed:.3f},{right_speed:.3f}\n"
        try:
            self.ser.write(command.encode("ascii"))
            self.get_logger().debug(f"Sent serial: {command.strip()}")
        except SerialException as exc:
            self.get_logger().warn(f"Serial write failed: {exc}")
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def destroy_node(self):
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoSerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
