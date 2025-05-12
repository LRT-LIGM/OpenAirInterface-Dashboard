from fastapi import FastAPI, HTTPException
import requests
import yaml
import os
import subprocess

app = FastAPI()

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
FIVEG_CORE_DOCKER_COMPOSE_PATH = os.getenv("FIVEG_CORE_DOCKER_COMPOSE_PATH", "/home/user/oai-cn5g/docker-compose.yaml")

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
    Restart the 5G core network using `docker compose`.

    This endpoint restarts the 5G core network by invoking the `docker compose restart`
    command with the specified Compose file, which stops and then restarts all services.

    Returns:
        dict: A dictionary containing:
            - message (str): A confirmation message if the core is restarted successfully.
            - stdout (str): Standard output from the docker compose command.
            - stderr (str): Standard error output from the docker compose command.
            - returncode (int): The return code from the subprocess execution.

    Raises:
        HTTPException: If the subprocess fails to execute the docker compose command
                       or if an unexpected error occurs.
    """
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", FIVEG_CORE_DOCKER_COMPOSE_PATH, "restart"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart the core network: {stderr}",
                headers={"X-Error": "Core Restart Error"}
            )

        return {
            "message": "Core network restarted successfully",
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode
        }

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
