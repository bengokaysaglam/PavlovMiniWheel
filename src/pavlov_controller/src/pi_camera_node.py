#!/usr/bin/env python3

import cv2
import rclpy
from rclpy.node import Node

def parse_device(device_value):
    if isinstance(device_value, str) and device_value.isdigit():
        return int(device_value)
    return device_value

def resolve_capture_backend(backend_name: str) -> int:
    """Resolve the preferred OpenCV backend and fall back to a usable one."""
    normalized = str(backend_name or "").strip().lower()
    candidate_names = [normalized] if normalized not in ("", "auto", "default", "any") else ["libcamera", "v4l2", "gstreamer", "any"]

    seen = set()
    for name in candidate_names:
        if name in ("", "auto", "default", "any"):
            value = cv2.CAP_ANY
        else:
            value = getattr(cv2, f"CAP_{name.upper()}", None)

        if isinstance(value, int) and value not in seen:
            seen.add(value)
            return int(value)

    return int(cv2.CAP_ANY)

def candidate_devices(device_value):
    """Return a practical device list for webcams and Pi cameras."""
    candidates = []

    if isinstance(device_value, (int, float)):
        candidates.append(int(device_value))
    elif isinstance(device_value, str):
        raw = device_value.strip()
        if raw.isdigit():
            candidates.append(int(raw))
        if raw:
            candidates.append(raw)

    for fallback in (0, "/dev/video0", "/dev/video1", "/dev/video2"):
        if fallback not in candidates:
            candidates.append(fallback)

    return candidates


class PiCameraNode(Node):
    def __init__(self):
        super().__init__("pi_camera_node")

        # Pi Camera V2 works best with the camera index 0 and the libcamera/auto backend
        # on Raspberry Pi OS, so use those as the defaults here.
        self.declare_parameter("device", 0)
        self.declare_parameter("output_path", "/tmp/pi_camera_v2_capture.jpg")
        self.declare_parameter("capture_backend", "auto")
        self.declare_parameter("image_width", 1640)
        self.declare_parameter("image_height", 1232)
        self.declare_parameter("frame_rate", 30.0)

        self.device = parse_device(self.get_parameter("device").value)
        self.output_path = self.get_parameter("output_path").value
        self.capture_backend = self.get_parameter("capture_backend").value
        self.image_width = int(self.get_parameter("image_width").value)
        self.image_height = int(self.get_parameter("image_height").value)
        self.frame_rate = float(self.get_parameter("frame_rate").value)

        self.capture_once()

    def capture_once(self) -> None:
        self.get_logger().info(
            f"Pi Camera V2 capture started: device={self.device}, backend={self.capture_backend}, "
            f"resolution={self.image_width}x{self.image_height}"
        )

        backend_candidates = []
        for backend_name in (str(self.capture_backend), "auto", "v4l2", "libcamera", "any"):
            backend = resolve_capture_backend(backend_name)
            if backend not in backend_candidates:
                backend_candidates.append(backend)

        device_candidates = candidate_devices(self.device)

        for backend in backend_candidates:
            for device in device_candidates:
                try:
                    cap = cv2.VideoCapture(device, backend)
                except Exception:
                    continue

                if not cap.isOpened():
                    try:
                        cap.release()
                    except Exception:
                        pass
                    continue

                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
                cap.set(cv2.CAP_PROP_FPS, self.frame_rate)

                success, frame = cap.read()
                if not success or frame is None:
                    cap.release()
                    continue

                saved = cv2.imwrite(self.output_path, frame)
                cap.release()

                if saved:
                    self.get_logger().info(f"Captured image saved to: {self.output_path}")
                else:
                    self.get_logger().error(f"Failed to save image to: {self.output_path}")
                return

        self.get_logger().error(
            f"Could not capture an image. Tried device={device_candidates} and backends={backend_candidates}."
        )


def main(args=None):
    rclpy.init(args=args)
    node = PiCameraNode()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

