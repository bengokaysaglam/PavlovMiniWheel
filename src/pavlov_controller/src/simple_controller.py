#!/usr/bin/env python3

import math
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.constants import S_TO_NS

from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Twist, TransformStamped
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry

from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler

class SimpleController(Node):

    def __init__(self):
        super().__init__("simple_controller")

        self.declare_parameter("wheel_radius", 0.0325)
        self.declare_parameter("wheel_separation", 0.1071)

        self.wheel_radius = self.get_parameter("wheel_radius").value
        self.wheel_separation = self.get_parameter("wheel_separation").value

        self.get_logger().info(f"Wheel radius: {self.wheel_radius}")
        self.get_logger().info(f"Wheel separation: {self.wheel_separation}")

        self.wheel_names = [
            "wheel_fl_joint",
            "wheel_fr_joint",
            "wheel_bl_joint",
            "wheel_br_joint",
        ]

        self.left_prev_pos = None
        self.right_prev_pos = None
        self.prev_time = None

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.wheel_cmd_pub = self.create_publisher(
            Float64MultiArray,
            "/simple_velocity_controller/commands",
            10
        )

        self.odom_pub = self.create_publisher(
            Odometry,
            "/odom",
            10
        )

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            "/cmd_vel",
            self.cmd_vel_callback,
            10
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_state_callback,
            10
        )

        self.tf_broadcaster = TransformBroadcaster(self)

    def cmd_vel_callback(self, msg):
        v = msg.linear.x
        w = msg.angular.z

        left_speed = (v - (w * self.wheel_separation / 2.0)) / self.wheel_radius
        right_speed = (v + (w * self.wheel_separation / 2.0)) / self.wheel_radius

        cmd = Float64MultiArray()

        cmd.data = [
            left_speed,    # wheel_fl_joint
            right_speed,   # wheel_fr_joint
            left_speed,    # wheel_bl_joint
            right_speed,   # wheel_br_joint
        ]

        self.wheel_cmd_pub.publish(cmd)

    def joint_state_callback(self, msg):
        for name in self.wheel_names:
            if name not in msg.name:
                return

        fl = msg.position[msg.name.index("wheel_fl_joint")]
        fr = msg.position[msg.name.index("wheel_fr_joint")]
        bl = msg.position[msg.name.index("wheel_bl_joint")]
        br = msg.position[msg.name.index("wheel_br_joint")]

        left_pos = (fl + bl) / 2.0
        right_pos = (fr + br) / 2.0

        current_time = Time.from_msg(msg.header.stamp)

        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            current_time = self.get_clock().now()

        if self.prev_time is None:
            self.prev_time = current_time
            self.left_prev_pos = left_pos
            self.right_prev_pos = right_pos
            return

        dt = current_time - self.prev_time
        dt_sec = dt.nanoseconds / S_TO_NS

        if dt_sec <= 0.0:
            return

        dp_left = left_pos - self.left_prev_pos
        dp_right = right_pos - self.right_prev_pos

        self.left_prev_pos = left_pos
        self.right_prev_pos = right_pos
        self.prev_time = current_time

        linear = self.wheel_radius * (dp_right + dp_left) / (2.0 * dt_sec)
        angular = self.wheel_radius * (dp_right - dp_left) / (self.wheel_separation * dt_sec)

        ds = self.wheel_radius * (dp_right + dp_left) / 2.0
        dtheta = self.wheel_radius * (dp_right - dp_left) / self.wheel_separation

        self.theta += dtheta
        self.x += ds * math.cos(self.theta)
        self.y += ds * math.sin(self.theta)

        q = quaternion_from_euler(0.0, 0.0, self.theta)

        now = self.get_clock().now().to_msg()

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]

        odom.twist.twist.linear.x = linear
        odom.twist.twist.angular.z = angular

        self.odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header.stamp = now
        tf.header.frame_id = "odom"
        tf.child_frame_id = "base_link"

        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.translation.z = 0.0

        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(tf)

def main(args=None):
    rclpy.init(args=args)

    node = SimpleController()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()