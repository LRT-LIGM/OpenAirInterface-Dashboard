import requests
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api import app

client = TestClient(app)

@patch("backend.api.requests.get")
def test_get_service_status_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": "success",
        "data": {
            "result": [
                {
                    "metric": {"status": "running"},
                    "value": [1234567890.0, "1"]
                }
            ]
        }
    }

    response = client.get("/core/amf/status")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}
# Test successful retrieval of AMF service status as "running".

@patch("backend.api.requests.get")
def test_get_service_status_metric_not_found(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": "success",
        "data": {"result": []}
    }

    response = client.get("/core/amf/status")
    assert response.status_code == 500
    assert "Metric not found" in response.text
# Test response when Prometheus returns an empty result (metric not found).

@patch("backend.api.requests.get")
def test_prometheus_unreachable(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
    response = client.get("/core/amf/status")

    assert response.status_code == 502
    assert "Prometheus unreachable" in response.json()["detail"]
# Test response when Prometheus is unreachable (connection error).
