from fastapi import FastAPI, HTTPException
import requests
import yaml
import os
import subprocess
from fastapi.responses import FileResponse
from tshark.capture_manager import CaptureManager

app = FastAPI()
manager = CaptureManager()

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

try:
    with open("config/monitored_services.yml", "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Error while loading the YAML file: {e}")
    config = {}


services_map = {entry["name"]: entry["container"] for entry in config["core_services"]}

def query_prometheus_status_only(container_name: str):
    """
    Query the Prometheus API to retrieve the status metric for a given container.

    Args:
        container_name (str): The name of the container to query within Prometheus.

    Returns:
        dict: A dictionary containing the container's status, for example: {"status": "running"}.

    Raises:
        HTTPException: If the metric is not found, the query fails, or the result is empty.
    """
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": f'oai_container_status{{container="{container_name}"}}'}
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] != "success" or not data["data"]["result"]:
            raise ValueError("Metric not found or empty")

        return {"status": data["data"]["result"][0]["metric"]["status"]}

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Bad Gateway: Prometheus unreachable. {e}")

    except (KeyError, IndexError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Invalid Prometheus response. {e}")

@app.post("/core/start")
def start_core_network():
    """
    Start the 5G core network using docker-compose.

    Returns:
        dict: Contains the result of the subprocess execution including stdout, stderr, and return code.
    """
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "/home/user/oai-cn5g/docker-compose.yaml", "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return {
            "message": "Core network started",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "Failed to start core network",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }
    except Exception as e:
        return {"error": "Unexpected error", "detail": str(e)}


@app.post("/core/stop")
def stop_core_network():
    """
    Stop the 5G core network using docker-compose.

    Returns:
        dict: Contains the result of the subprocess execution including stdout, stderr, and return code.
    """
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "/home/user/oai-cn5g/docker-compose.yaml", "down"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return {
            "message": "Core network stopped",
            "stdout": result.stdout.decode('utf-8'),
            "stderr": result.stderr.decode('utf-8'),
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": "Failed to stop core network",
            "stdout": e.stdout.decode('utf-8'),
            "stderr": e.stderr.decode('utf-8'),
            "returncode": e.returncode
        }
    except Exception as e:
        return {"error": "Unexpected error", "detail": str(e)}




@app.get("/core/{service_name}/status")
def get_service_status(service_name: str):
    """
    Retrieve the status of a core service based on its service name.

    Args:
        service_name (str): The unique name of the core service to query.

    Returns:
        dict: A dictionary containing the status of the requested core service.

    Raises:
        HTTPException: If the service name does not exist in the monitored services
                       or if an error occurs during the Prometheus query.
    """
    if service_name not in services_map:
        raise HTTPException(status_code=404, detail="Service not found")
    container = services_map[service_name]
    return query_prometheus_status_only(container)


def start_network():
    """
    Endpoint to start the core network using Docker Compose.

    Returns:
        dict: A dictionary with a success message when the network is started.
    """
    return start_core_network()


def stop_network():
    """
    Endpoint to stop the core network using Docker Compose.

    Returns:
        dict: A dictionary with a success message when the network is stopped.
    """
    return stop_core_network()



@app.post("/wireshark/start")
def start(interface: str = "eth0"):
    try:
        file_path = manager.start_capture(interface)
        return {"message": f"Capture started on {interface}", "file": file_path}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wireshark/stop")
def stop():
    try:
        file_path = manager.stop_capture()
        return {"message": "Capture stopped", "file": file_path}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wireshark/download")
def download():
    if not manager.capture_file or not os.path.exists(manager.capture_file):
        raise HTTPException(status_code=404, detail="No capture file available")
    return FileResponse(manager.capture_file, media_type="application/octet-stream", filename="capture.pcap")
