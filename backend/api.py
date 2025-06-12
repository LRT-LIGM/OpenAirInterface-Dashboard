from fastapi import FastAPI, HTTPException, WebSocket, Query
from starlette.websockets import WebSocketDisconnect
from backend.wireshark.packet_manager import capture_packets
from backend.gnb_manager.gnodeb_manager import GNodeBManager
import requests
import yaml
import os
import asyncio
import subprocess
import logging
from pathlib import Path
from backend.influx.influx_config import  query_api, INFLUXDB_ORG, INFLUXDB_BUCKET
import time

logger = logging.getLogger("metrics_websocket")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
FIVEG_CORE_DOCKER_COMPOSE_PATH = os.getenv("FIVEG_CORE_DOCKER_COMPOSE_PATH", "/home/user/oai-cn5g/docker-compose.yaml")
GNB_CONFIG_PATH = os.getenv("GNB_CONFIG_PATH","/home/user/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/oaibox.yaml")
GNB_EXECUTABLE = os.getenv("GNB_EXECUTABLE","/home/user/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem")
CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "/home/user/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF"))
METRIC_POLL_INTERVAL_SECONDS = int(os.getenv("METRIC_POLL_INTERVAL_SECONDS", 2))

gnb = GNodeBManager(config_path=GNB_CONFIG_PATH, executable_path=GNB_EXECUTABLE)

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
    Start the 5G core network using `docker compose`.

    This endpoint launches the 5G core services defined in the Docker Compose file.
    It uses a subprocess to run the `docker compose up -d` command, which starts
    the containers in detached mode.

    Returns:
        dict: A dictionary containing:
            - message (str): A confirmation message if the core starts successfully.
            - stdout (str): Standard output from the docker compose command.
            - stderr (str): Standard error output from the docker compose command.
            - returncode (int): The return code from the subprocess execution.

    Raises:
        HTTPException: If the subprocess fails to execute the docker compose command
                       or an unexpected error occurs.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", FIVEG_CORE_DOCKER_COMPOSE_PATH, "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return {
            "message": "Core network started",
            "stdout": result.stdout.decode('utf-8'),
            "stderr": result.stderr.decode('utf-8'),
            "returncode": result.returncode
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start the core network: {e.stderr.decode('utf-8')}",
            headers={"X-Error": "Subprocess Error"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
            headers={"X-Error": "Unexpected Error"}
        )

@app.post("/core/stop")
def stop_core_network():
    """
    Stop the 5G core network using `docker compose`.

    This endpoint stops all running 5G core services by executing the
    `docker compose down` command using a subprocess. It stops and removes
    the containers, networks, and other resources defined in the Docker Compose file.

    Returns:
        dict: A dictionary containing:
            - message (str): A confirmation message if the core is stopped successfully.
            - stdout (str): Standard output from the docker compose command.
            - stderr (str): Standard error output from the docker compose command.
            - returncode (int): The return code from the subprocess execution.

    Raises:
        HTTPException: If the subprocess fails to execute the docker compose command
                       or an unexpected error occurs during the process.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", FIVEG_CORE_DOCKER_COMPOSE_PATH, "down"],
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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop the core network: {e.stderr.decode('utf-8')}",
            headers={"X-Error": "Subprocess Error"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
            headers={"X-Error": "Unexpected Error"}
        )

@app.post("/core/restart")
def restart_core_network():
    """
    Restart the 5G core network by stopping it, waiting 4 seconds,
    then starting it again.

    Returns:
        dict: A dictionary containing the combined result of stopping
              and starting the core network, with their respective
              stdout, stderr, and return codes.

    Raises:
        HTTPException: If an error occurs during stop or start subprocess execution.
    """
    try:
        stop_result = stop_core_network()
        time.sleep(4)
        start_result = start_core_network()

        return {
            "message": "Core network restarted successfully",
            "stop": stop_result,
            "start": start_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during restart: {str(e)}",
            headers={"X-Error": "Unexpected Error"}
        )

@app.get("/core/{service_name}/status")
def get_service_status(service_name: str):
    """
    Retrieve the status of a core service based on its service name.

    This endpoint maps the service name to a container name defined in the configuration
    file and queries Prometheus for its current runtime status.

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

@app.websocket("/ws/pcap")
async def live_packet_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live network packet capture.

    Establishes a WebSocket connection with the client and starts capturing network
    packets in real time using PyShark. The capture is performed on a specified
    network interface (default: "eth0"), and can be optionally filtered using a
    BPF (Berkeley Packet Filter) expression (example : "udp", "ip").

    The interface and filter can be provided as query parameters:
        - interface (str): the name of the network interface to capture from. Default is "eth0"
        - bpf_filter (str): an optional BPF filter expression. Default is no filter

    Args:
        websocket (WebSocket): The WebSocket connection with the client.

    Returns:
        None: The captured packets are streamed live to the client over the WebSocket connection.

    Raises:
        None directly, but connection may close automatically if PyShark encounters an error
        (example : invalid BPF syntax, interface not found, etc.).
    """
    await websocket.accept()

    interface = websocket.query_params.get("interface", "eth0")
    bpf_filter = websocket.query_params.get("bpf_filter", "")

    logging.info(f"New WebSocket connection: interface={interface}, bpf_filter={bpf_filter}")

    await capture_packets(websocket, interface=interface, bpf_filter=bpf_filter)

@app.post("/gnb/stop")
def stop_gnb():
    """
    Stops the gNB process using the GNodeB instance.

    Returns:
        dict: Status message and the PID of the stopped process.

    Raises:
        HTTPException: If the gNB is not running or cannot be stopped.
    """
    try:
        pid = gnb.stop()
        return {"status": f"gNB process {pid} stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop gNB: {str(e)}")

@app.post("/gnb/start")
async def start_gnb():
    """
    Starts the gNB process using the GNodeB instance.

    Returns:
        dict: Status message and the PID of the started process.

    Raises:
        HTTPException: If the gNB fails to start.
    """
    try:
        await gnb.start()
        return {"status": "gNB started", "pid": gnb.process.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/gnb")
async def websocket_pcap(websocket: WebSocket):
    """
    WebSocket endpoint to stream real-time gNB logs to connected clients.

    - Accepts the WebSocket connection.
    - Sends stdout log lines from the gNB if it is running.
    - Closes the connection if the gNB stops or the client disconnects.

    Args:
        websocket (WebSocket): The active WebSocket connection.
    """
    await websocket.accept()

    if not gnb.is_running():
        await websocket.send_text("gNB process is not running.")
        await websocket.close()
        return

    try:
        while True:
            if not gnb.is_running():
                await websocket.send_text("gNB process ended.")
                break

            try:
                line = await asyncio.wait_for(gnb.stdout_queue.get(), timeout=1.0)
                await websocket.send_text(line)
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        print("Client disconnected from /ws/gnb")

@app.get("/gnb/config")
def show_gnb_config():
    """
    Return a list of all .yaml or .conf files that contain 'gnb' in their name
    from the predefined configuration directory.

    Returns:
        dict: A dictionary with a list of matching file names.
    """
    try:
        if not CONFIG_DIR.exists():
            raise HTTPException(status_code=500, detail="Invalid CONFIG_DIR: directory does not exist.")

        files = [
            f.name for f in CONFIG_DIR.iterdir()
            if f.is_file() and "gnb" in f.name.lower() and f.suffix in [".yaml", ".conf"]
        ]

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list config files: {str(e)}")

@app.websocket("/ws/metrics")
async def websocket_latest_metrics(
    websocket: WebSocket,
    metric_name: str = Query(..., description="The name of the metric to fetch"),
    ue_id: str = Query(..., description="The ID of the User Equipment (UE)")
):
    """
    WebSocket endpoint to stream real-time metrics from InfluxDB for a specific User Equipment (UE).

    Query Parameters:
    - metric_name (str): The name of the metric to retrieve (e.g., "cpu", "ram").
    - ue_id (str): The identifier of the User Equipment.

    Behavior:
    - Accepts a WebSocket connection.
    - Polls InfluxDB every `METRIC_POLL_INTERVAL_SECONDS` seconds.
    - On the first request, queries data from the last 10 seconds.
    - On subsequent requests, fetches only new data with `_time` strictly greater than the last sent timestamp.
    - Sends the latest data point to the client if a new value is available.
    - Skips sending if no newer value is present since the last transmission.

    Implementation Details:
    - Uses Flux queries with time-based filtering to avoid duplicate or stale data.
    - Remembers the last sent timestamp and only pushes data with a more recent timestamp.
    - Ensures efficient use of bandwidth and reduces redundant WebSocket messages.

    Error Handling:
    - Logs and returns an error message to the client if the InfluxDB query fails.
    - Gracefully closes the WebSocket if the client disconnects.

    Notes:
    - This endpoint is optimized for time-series streaming with minimal latency.
    - Assumes that each new value in InfluxDB has a unique and increasing `_time` field.
    """

    await websocket.accept()
    last_sent_time = None

    try:
        while True:
            # Build the query depending on whether we already have a last piece of data sent
            if last_sent_time is None:
                # First query, take data from the last 10 seconds
                time_filter = 'range(start: -10s)'
            else:
                # For the following, we filter on _time > last_sent_time to only take new ones
                time_filter = f'range(start: {last_sent_time.isoformat()}) |> filter(fn: (r) => r._time > time(v: "{last_sent_time.isoformat()}"))'

            query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                |> {time_filter}
                |> filter(fn: (r) => 
                    r["_measurement"] == "system_usage" and
                    r["ue_id"] == "{ue_id}" and
                    r["_field"] == "{metric_name}"
                )
                |> last()
            '''

            loop = asyncio.get_running_loop()
            try:
                tables = await loop.run_in_executor(None, query_api.query, query, INFLUXDB_ORG)

            except Exception as e:
                logger.error(f"InfluxDB query failed: {e}")
                await websocket.send_json({"error": "Internal server error while querying metrics."})
                await websocket.close(code=1011)  # 1011: Internal Error
                break

            for table in tables:
                for record in table.records:
                    timestamp = record.get_time()
                    value = record.get_value()

                    # If we have already initialized, we only send if new data
                    if (last_sent_time is None) or (timestamp > last_sent_time):
                        await websocket.send_json({
                            "ue_id": ue_id,
                            "metric": metric_name,
                            "value": value,
                            "timestamp": str(timestamp)
                        })
                        last_sent_time = timestamp
                        logger.info(f"[SEND] {ue_id} {metric_name} = {value} at {timestamp}")

            await asyncio.sleep(METRIC_POLL_INTERVAL_SECONDS)

    except WebSocketDisconnect:
        logger.info(f"[DISCONNECT] WebSocket closed for UE {ue_id}, metric {metric_name}")