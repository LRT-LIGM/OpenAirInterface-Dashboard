import subprocess
import os
from datetime import datetime

class CaptureManager:
    def __init__(self):
        self.process = None
        self.capture_file = None

    def start_capture(self, interface="eth0"):
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
        if not self.process:
            raise RuntimeError("No capture running")

        self.process.terminate()
        self.process.wait()
        self.process = None
        return self.capture_file