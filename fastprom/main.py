from fastapi import FastAPI, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import docker

app = FastAPI()
client = docker.from_env()

containers = ["oai-upf", "oai-smf", "oai-amf", "oai-ausf", "oai-udm", "oai-udr", "oai-nssf", "oai-nrf", "ims","oai-next-dn", "openspeedtest"]

registries = {}
gauges = {}

for name in containers:
    reg = CollectorRegistry()
    g = Gauge("oai_container_status", f"{name} container status", ["container", "status"], registry=reg)
    registries[name] = reg
    gauges[name] = g

def update_container_status(container_name):
    gauge = gauges[container_name]
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
    container_name = component if component in ["ims", "openspeedtest"] else f"oai-{component}"
    if container_name not in registries:
        return Response(status_code=404, content=f"Unknown component: {component}")
    update_container_status(container_name)
    data = generate_latest(registries[container_name])
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

