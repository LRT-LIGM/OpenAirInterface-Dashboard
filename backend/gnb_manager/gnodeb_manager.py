import asyncio
import subprocess
import os
import signal
from pathlib import Path

class GNodeBManager:
    """
    Represents a gNodeB (gNB) instance with process control and real-time log handling.

    Attributes:
        process (subprocess.Popen): The currently running gNB process.
        stdout_queue (asyncio.Queue): Queue for capturing stdout lines from the gNB.

    Methods:
        start(): Starts the gNB process using the given configuration.
        stop(): Gracefully stops the gNB process using SIGTERM.
        is_running(): Checks if the gNB process is still running.
    """

    def __init__(self, config_path: str, executable_path: str):
        self.config_path = Path(config_path)
        self.executable_path = Path(executable_path)
        self.process = None
        self.stdout_queue = asyncio.Queue()

    async def start(self):
        """
        Starts the gNB process using the provided configuration file.

        - Verifies that the config file and executable exist.
        - Launches the process using subprocess.
        - Creates an asynchronous task to read and enqueue stdout lines.

        Raises:
            RuntimeError: If the gNB is already running.
            FileNotFoundError: If the config or executable file does not exist.
            Exception: For other process launch errors.
        """
        if self.process is not None:
            raise RuntimeError("gNB already running")

        if not self.config_path.is_file():
            raise FileNotFoundError("Configuration file not found.")

        if not self.executable_path.is_file():
            raise FileNotFoundError("gNB executable not found.")

        self.process = subprocess.Popen(
            [
                str(self.executable_path),
                "-O", str(self.config_path),
                "--gNBs.[0].min_rxtxtime", "6",
                "-E",
                "--continuous-tx",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        asyncio.create_task(self._stream_stdout_to_queue())

    async def _stream_stdout_to_queue(self):
        """
        Continuously reads the gNB process's stdout and puts each line into the stdout queue.

        This is run as a background async task and allows real-time streaming of logs to WebSocket clients.
        """
        while True:
            line = await asyncio.to_thread(self.process.stdout.readline)
            if not line:
                break
            await self.stdout_queue.put(line)

    def stop(self):
        """
        Stops the running gNB process by sending a SIGTERM signal.

        Returns:
            int: The PID of the process that was terminated.

        Raises:
            RuntimeError: If no gNB process is currently running.
            PermissionError: If the process cannot be terminated due to permissions.
            Exception: For any other stopping error.
        """
        if self.process is None:
            raise RuntimeError("gNB not running")

        try:
            os.kill(self.process.pid, signal.SIGTERM)
            pid = self.process.pid
            self.process = None
            return pid
        except ProcessLookupError:
            self.process = None
            raise RuntimeError("Process does not exist.")
        except PermissionError:
            raise PermissionError("Permission denied.")
        except Exception as e:
            raise RuntimeError(str(e))

    def is_running(self):
        """
        Checks if the gNB process is currently running.

        Returns:
            bool: True if the process is active, False otherwise.
        """
        return self.process is not None and self.process.poll() is None
