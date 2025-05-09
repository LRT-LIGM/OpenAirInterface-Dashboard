import subprocess
import os
from datetime import datetime

class CaptureManager:
    """
    Manage network traffic captures using Tshark. This class provides
    methods to start and stop a capture process, and keeps track of the
    current capture file path.
    """
    def __init__(self):
        """
            Initialize the CaptureManager.

            Attributes:
                process (subprocess.Popen | None): Reference to the tshark subprocess.
                capture_file (str | None): Path to the capture file being written.
        """
        self.process = None
        self.capture_file = None

    def start_capture(self, interface="eth0"):
        """
        Start a tshark capture on the specified network interface.

        Args:
            interface (str): Name of the network interface to capture from (default: "eth0").

        Returns:
            str: Path to the capture file.

        Raises:
            RuntimeError: If a capture is already running.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_dir = "tshark/captures"
        os.makedirs(capture_dir, exist_ok=True)
        self.capture_file = f"{capture_dir}/capture_{interface}_{timestamp}.pcap"
        if self.process:
            raise RuntimeError("Capture already running")

        self.process = subprocess.Popen([
            "tshark", "-i", interface, "-w", self.capture_file
        ])
        return self.capture_file

    def stop_capture(self):
        """
        Stop the current tshark capture.

        Returns:
            str: Path to the saved capture file.

        Raises:
            RuntimeError: If no capture is currently running.
        """
        if not self.process:
            raise RuntimeError("No capture running")

        self.process.terminate()
        self.process.wait()
        self.process = None
        return self.capture_file