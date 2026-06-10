import importlib.util
from pathlib import Path

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
