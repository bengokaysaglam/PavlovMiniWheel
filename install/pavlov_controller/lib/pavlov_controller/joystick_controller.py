#!/usr/bin/env python3

import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class JoystickController(Node):

    def __init__(self):
        super().__init__('joystick_controller')

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/pavlov_controller/cmd_vel',
            10
        )

        self.linear_speed = 0.5
        self.angular_speed = 1.0

        self.get_logger().info('WASD Keyboard Controller Başlatıldı!')
        self.get_logger().info('W: İleri')
        self.get_logger().info('S: Geri')
        self.get_logger().info('A: Sol')
        self.get_logger().info('D: Sağ')
        self.get_logger().info('Q: Çıkış')

        self.run_keyboard_loop()

    def get_key(self):
        """
        Terminalden tek karakter oku
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return key

    def run_keyboard_loop(self):

        while rclpy.ok():

            key = self.get_key()

            twist = Twist()

            # İLERİ
            if key == 'w':
                twist.linear.x = self.linear_speed

            # GERİ
            elif key == 's':
                twist.linear.x = -self.linear_speed

            # SOLA DÖN
            elif key == 'a':
                twist.angular.z = self.angular_speed

            # SAĞA DÖN
            elif key == 'd':
                twist.angular.z = -self.angular_speed

            # ÇIKIŞ
            elif key == 'q':
                self.get_logger().info('Çıkılıyor...')
                break

            # STOP
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0

            self.cmd_vel_pub.publish(twist)

            self.get_logger().info(
                f'Linear: {twist.linear.x:.2f}, Angular: {twist.angular.z:.2f}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = JoystickController()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()