from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

PROMETHEUS_URL = "http://prometheus:9090"

def query_prometheus_status_only(container_name: str):
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": f'oai_container_status{{container="{container_name}"}}'}
        )
        data = response.json()
        if data["status"] != "success" or not data["data"]["result"]:
            raise ValueError("Metric not found or empty")
        return {"status": data["data"]["result"][0]["metric"]["status"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/core/upf/status")
def get_upf_status():
    return query_prometheus_status_only("oai-upf")

@app.get("/core/smf/status")
def get_smf_status():
    return query_prometheus_status_only("oai-smf")

@app.get("/core/amf/status")
def get_amf_status():
    return query_prometheus_status_only("oai-amf")

@app.get("/core/ausf/status")
def get_ausf_status():
    return query_prometheus_status_only("oai-ausf")

@app.get("/core/udm/status")
def get_udm_status():
    return query_prometheus_status_only("oai-udm")

@app.get("/core/udr/status")
def get_udr_status():
    return query_prometheus_status_only("oai-udr")

@app.get("/core/nssf/status")
def get_nssf_status():
    return query_prometheus_status_only("oai-nssf")

@app.get("/core/nrf/status")
def get_nrf_status():
    return query_prometheus_status_only("oai-nrf")

@app.get("/core/ims/status")
def get_ims_status():
    return query_prometheus_status_only("ims")
