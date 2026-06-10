import importlib.util
from pathlib import Path

import pytest

module_path = Path(__file__).resolve().parents[1] / "src" / "pi_camera_node.py"
spec = importlib.util.spec_from_file_location("pi_camera_node", module_path)
pi_camera_node = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pi_camera_node)


def test_parse_device_accepts_numeric_strings():
    assert pi_camera_node.parse_device("0") == 0
    assert pi_camera_node.parse_device("/dev/video0") == "/dev/video0"


def test_resolve_capture_backend_auto_returns_valid_backend():
    backend = pi_camera_node.resolve_capture_backend("auto")

    assert isinstance(backend, int)
    assert backend >= 0


def test_open_camera_handles_logger_error_without_format_args(monkeypatch):
    class FakeLogger:
        def __init__(self):
            self.messages = []

        def error(self, msg, *args):
            if args:
                raise TypeError("logger.error does not accept format arguments")
            self.messages.append(msg)

    class FakeCapture:
        def isOpened(self):
            return False

        def release(self):
            return None

    dummy = object.__new__(pi_camera_node.PiCameraNode)
    dummy.cap = None
    dummy.capture_backend = "v4l2"
    dummy.device = "/dev/video0"
    dummy.image_width = 640
    dummy.image_height = 480
    dummy.frame_rate = 30.0
    dummy.get_logger = lambda: FakeLogger()

    monkeypatch.setattr(pi_camera_node.cv2, "VideoCapture", lambda *args, **kwargs: FakeCapture())

    dummy._open_camera()

    assert dummy.cap is None
