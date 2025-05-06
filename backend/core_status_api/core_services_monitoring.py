from fastapi import FastAPI, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import docker
import yaml

app = FastAPI()
client = docker.from_env()

try:
    with open("config/monitored_services.yml", "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Error while loading the YAML file: {e}")
    config = {}

services_map = {entry["name"]: entry["container"] for entry in config["core_services"]}

registries = {}
gauges = {}

for name, container_name in services_map.items():
    reg = CollectorRegistry()
    g = Gauge("oai_container_status", f"{container_name} container status", ["container", "status"], registry=reg)
    registries[name] = reg
    gauges[name] = g

def update_container_status(name):
    """
    Update the Prometheus gauge with the current status of the specified Docker container.

    Args:
        name (str): The service name defined in the monitored services configuration.

    Returns:
        None

    Side Effects:
        Updates the corresponding Prometheus gauge with one of the following statuses:
        - running
        - exited
        - not_found
        - error
    """
    container_name = services_map[name]
    gauge = gauges[name]
    try:
        container = client.containers.get(container_name)
        status = container.status
    except docker.errors.NotFound:
        status = "not_found"
    except Exception:
        status = "error"

    gauge.clear()
    gauge.labels(container=container_name, status=status).set(1)

@app.get("/metrics/{component}")
def get_metrics(component: str):
    """
    Retrieve Prometheus-formatted metrics for a given monitored component.

    Args:
        component (str): The name of the monitored component, as defined in the configuration.

    Returns:
        Response: A Prometheus-compatible HTTP response with container status metrics.
                  If the component is not found, returns a 404 response.

    Raises:
        None directly, but returns a 404 response if the component is unknown.
    """
    if component not in services_map:
        return Response(status_code=404, content=f"Unknown component: {component}")

    update_container_status(component)
    data = generate_latest(registries[component])
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
