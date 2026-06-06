#!/usr/bin/env python3

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


def parse_device(device_value):
    if isinstance(device_value, str) and device_value.isdigit():
        return int(device_value)
    return device_value


def camera_backend_constant(backend_name: str):
    if not backend_name:
        return cv2.CAP_ANY

    attr_name = f"CAP_{backend_name.upper()}"
    return getattr(cv2, attr_name, cv2.CAP_ANY)


class PiCameraNode(Node):
    def __init__(self):
        super().__init__("pi_camera_node")

        self.declare_parameter("device", "/dev/video0")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("camera_info_topic", "/camera/camera_info")
        self.declare_parameter("camera_frame_id", "camera_link")
        self.declare_parameter("image_width", 640)
        self.declare_parameter("image_height", 480)
        self.declare_parameter("frame_rate", 30.0)
        self.declare_parameter("fx", 530.47)
        self.declare_parameter("fy", 529.08)
        self.declare_parameter("cx", 320.0)
        self.declare_parameter("cy", 240.0)
        self.declare_parameter("distortion_coefficients", [0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter("distortion_model", "plumb_bob")
        self.declare_parameter("capture_backend", "v4l2")

        self.device = parse_device(self.get_parameter("device").value)
        self.image_topic = self.get_parameter("image_topic").value
        self.camera_info_topic = self.get_parameter("camera_info_topic").value
        self.camera_frame_id = self.get_parameter("camera_frame_id").value
        self.image_width = int(self.get_parameter("image_width").value)
        self.image_height = int(self.get_parameter("image_height").value)
        self.frame_rate = float(self.get_parameter("frame_rate").value)
        self.fx = float(self.get_parameter("fx").value)
        self.fy = float(self.get_parameter("fy").value)
        self.cx = float(self.get_parameter("cx").value)
        self.cy = float(self.get_parameter("cy").value)
        self.distortion_coefficients = list(self.get_parameter("distortion_coefficients").value)
        self.distortion_model = self.get_parameter("distortion_model").value
        self.capture_backend = self.get_parameter("capture_backend").value

        self._bridge = CvBridge()
        self._camera_info_msg = self._build_camera_info()

        self._image_pub = self.create_publisher(Image, self.image_topic, 10)
        self._camera_info_pub = self.create_publisher(CameraInfo, self.camera_info_topic, 10)

        self.cap = None
        self._open_camera()

        timer_period = max(1.0 / max(self.frame_rate, 1.0), 1.0 / 60.0)
        self._timer = self.create_timer(timer_period, self._timer_callback)

        self.get_logger().info(
            f"PiCameraNode ready: device={self.device} topic={self.image_topic} info={self.camera_info_topic} "
            f"resolution={self.image_width}x{self.image_height} fps={self.frame_rate}"
        )

    def _build_camera_info(self) -> CameraInfo:
        msg = CameraInfo()
        msg.header.frame_id = self.camera_frame_id
        msg.width = self.image_width
        msg.height = self.image_height
        msg.distortion_model = str(self.distortion_model)
        msg.d = [float(x) for x in self.distortion_coefficients]
        msg.k = [self.fx, 0.0, self.cx, 0.0, self.fy, self.cy, 0.0, 0.0, 1.0]
        msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        msg.p = [self.fx, 0.0, self.cx, 0.0, 0.0, self.fy, self.cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        return msg

    def _open_camera(self) -> None:
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass

        backend = camera_backend_constant(str(self.capture_backend))
        self.cap = cv2.VideoCapture(self.device, backend)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.frame_rate)

        if not self.cap.isOpened():
            self.get_logger().error(
                f"Cannot open camera device {self.device} with backend {self.capture_backend}."
            )
            self.cap = None
        else:
            self.get_logger().info(f"Camera opened: {self.device} using backend {self.capture_backend}")

    def _timer_callback(self) -> None:
        if self.cap is None:
            self._open_camera()
            return

        success, frame = self.cap.read()
        if not success or frame is None:
            self.get_logger().warn("Camera read failed; retrying.")
            self.cap.release()
            self.cap = None
            return

        try:
            image_msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        except Exception as exc:
            self.get_logger().error(f"Failed to convert image: {exc}")
            return

        stamp = self.get_clock().now().to_msg()
        image_msg.header.stamp = stamp
        image_msg.header.frame_id = self.camera_frame_id

        camera_info = CameraInfo()
        camera_info.header.stamp = stamp
        camera_info.header.frame_id = self.camera_frame_id
        camera_info.width = self.image_width
        camera_info.height = self.image_height
        camera_info.distortion_model = self._camera_info_msg.distortion_model
        camera_info.d = self._camera_info_msg.d
        camera_info.k = self._camera_info_msg.k
        camera_info.r = self._camera_info_msg.r
        camera_info.p = self._camera_info_msg.p

        self._image_pub.publish(image_msg)
        self._camera_info_pub.publish(camera_info)

    def destroy_node(self) -> None:
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PiCameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
