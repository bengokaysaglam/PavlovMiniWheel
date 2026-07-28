#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import PoseStamped, PointStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Bool

class BallToGoal(Node):
    def __init__(self) -> None:
        super().__init__("ball_to_goal")

        self.declare_parameter("ball_point_topic", "/ball/point")
        self.declare_parameter("ball_visible_topic", "/ball/visible")
        self.declare_parameter("goal_topic", "/goal_pose")

        self.declare_parameter("publish_rate_hz", 7.5)
        self.declare_parameter("visible_timeout_sec", 0.6)

        self.declare_parameter("standoff_m", 0.25)
        self.declare_parameter("min_ball_x_m", 0.15)
        self.declare_parameter("max_goal_x_m", 6.0)
        self.declare_parameter("max_goal_y_m", 2.0)
        self.declare_parameter("goal_frame", "base_link")

        self._ball_visible = False
        self._last_visible_time = None

        self._last_ball_point = None
        self._last_ball_time = None

        self._goal_pub = self.create_publisher(PoseStamped, str(self.get_parameter("goal_topic").value), 10)

        ball_point_topic = str(self.get_parameter("ball_point_topic").value)
        ball_visible_topic = str(self.get_parameter("ball_visible_topic").value)
        self.get_logger().debug(f"Subscribing to: ball_point={ball_point_topic}, visible={ball_visible_topic}")

        self.create_subscription(
            Bool,
            ball_visible_topic,
            self._visible_cb,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            PointStamped,
            ball_point_topic,
            self._ball_point_cb,
            qos_profile_sensor_data,
        )

        publish_rate_hz = float(self.get_parameter("publish_rate_hz").value or 7.5)
        timer_period = 1.0 / max(publish_rate_hz, 0.5)
        self._timer = self.create_timer(timer_period, self._tick)
        self.get_logger().debug(f"Timer created: period={timer_period:.3f}s (rate={publish_rate_hz} Hz)")

        self.get_logger().info(
            "BALL_TO_GOAL READY | "
            f"ball={self.get_parameter('ball_point_topic').value} "
            f"visible={self.get_parameter('ball_visible_topic').value} "
            f"goal_out={self.get_parameter('goal_topic').value}"
        )

    def _visible_cb(self, msg: Bool) -> None:
        self._ball_visible = bool(msg.data)
        self._last_visible_time = self.get_clock().now()
        self.get_logger().debug(f"Visible callback: ball_visible={self._ball_visible}")

    def _ball_point_cb(self, msg: PointStamped) -> None:
        self._last_ball_point = msg
        self._last_ball_time = msg.header.stamp if msg.header.stamp.nanosec != 0 or msg.header.stamp.sec != 0 else self.get_clock().now()
        self.get_logger().debug(f"Ball point callback: x={msg.point.x:.3f}, y={msg.point.y:.3f}")

    def _is_fresh(self, stamp, timeout_sec: float) -> bool:
        if stamp is None:
            return False
        
        now = self.get_clock().now()
        
        # stamp bir ROS mesajından gelen Time nesnesiyse (sec ve nanosec içerir)
        if hasattr(stamp, 'sec') and hasattr(stamp, 'nanosec'):
            stamp_sec = stamp.sec + stamp.nanosec * 1e-9
        # rclpy.time.Time nesnesiyse (nanoseconds içeriyorsa)
        elif hasattr(stamp, 'nanoseconds'):
            stamp_sec = stamp.nanoseconds * 1e-9
        else:
            # Eğer düz bir float veya int saniye değeriyse
            stamp_sec = float(stamp)
            
        now_sec = now.nanoseconds * 1e-9
        age = now_sec - stamp_sec
        
        return age <= timeout_sec

    def _tick(self) -> None:
        self.get_logger().debug("_tick() called")
        visible_timeout_sec = float(self.get_parameter("visible_timeout_sec").value or 0.6)

        ball_fresh = self._is_fresh(self._last_ball_time, visible_timeout_sec)
        visible_fresh = self._is_fresh(self._last_visible_time, visible_timeout_sec)

        self.get_logger().debug(f"ball_fresh={ball_fresh}, visible_fresh={visible_fresh}, ball_visible={self._ball_visible}, last_ball_point={self._last_ball_point is not None}")

        if not ball_fresh:
            self.get_logger().warn(f"[DEBUG] Ball point is stale - last_time={self._last_ball_time}, timeout={visible_timeout_sec}s", throttle_duration_sec=2.0)
            return
        if not visible_fresh:
            self.get_logger().warn(f"[DEBUG] Visible flag is stale - last_time={self._last_visible_time}, timeout={visible_timeout_sec}s", throttle_duration_sec=2.0)
            return
        if not self._ball_visible:
            self.get_logger().warn("[DEBUG] Ball flag is false", throttle_duration_sec=2.0)
            return
        if self._last_ball_point is None:
            self.get_logger().warn("[DEBUG] Ball point message is missing", throttle_duration_sec=2.0)
            return

        p = self._last_ball_point.point
        ball_x = float(p.x)
        ball_y = float(p.y)

        self.get_logger().debug(f"Ball point: x={ball_x:.3f}, y={ball_y:.3f}")

        standoff_m = float(self.get_parameter("standoff_m").value or 0.25)
        min_ball_x_m = float(self.get_parameter("min_ball_x_m").value or 0.15)
        max_goal_x_m = float(self.get_parameter("max_goal_x_m").value or 6.0)
        max_goal_y_m = float(self.get_parameter("max_goal_y_m").value or 2.0)
        goal_frame = str(self.get_parameter("goal_frame").value)

        if not math.isfinite(ball_x) or not math.isfinite(ball_y):
            self.get_logger().warn(f"Ball coordinates not finite: x={ball_x}, y={ball_y}")
            return

        if ball_x < min_ball_x_m:
            self.get_logger().warn(f"Ball x={ball_x:.3f} is too close (min={min_ball_x_m:.3f})")
            return

        goal_x = max(0.0, ball_x - standoff_m)
        goal_y = ball_y

        goal_x = min(goal_x, max_goal_x_m)
        goal_y = max(-max_goal_y_m, min(max_goal_y_m, goal_y))

        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = goal_frame
        goal.pose.position.x = goal_x
        goal.pose.position.y = goal_y
        goal.pose.position.z = 0.0

        goal.pose.orientation.x = 0.0
        goal.pose.orientation.y = 0.0
        goal.pose.orientation.z = 0.0
        goal.pose.orientation.w = 1.0

        self.get_logger().info(f"[DEBUG] Publishing goal: x={goal_x:.3f}, y={goal_y:.3f}, frame={goal_frame}")
        self._goal_pub.publish(goal)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = BallToGoal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

if __name__ == "__main__":
    main()