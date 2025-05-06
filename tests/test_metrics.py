from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.core_status_api.core_services_monitoring import app

client = TestClient(app)

@patch("backend.core_status_api.core_services_monitoring.client")
def test_metrics_amf_running(mock_docker_client):
    mock_container = MagicMock()
    mock_container.status = "running"
    mock_docker_client.containers.get.return_value = mock_container
    response = client.get("/metrics/amf")

    assert response.status_code == 200
    assert b'oai_container_status' in response.content
    assert b'amf' in response.content
    assert b'running' in response.content
# Test if the metrics for AMF are correctly returned when the container is running.

@patch("backend.core_status_api.core_services_monitoring.client")
def test_metrics_amf_container_not_found(mock_docker_client):
    from docker.errors import NotFound
    mock_docker_client.containers.get.side_effect = NotFound("not found")
    response = client.get("/metrics/amf")

    assert response.status_code == 200
    assert b'not_found' in response.content
# Test if the API returns 'not_found' when the AMF container doesn't exist.

@patch("backend.core_status_api.core_services_monitoring.client")
def test_metrics_amf_docker_error(mock_docker_client):
    mock_docker_client.containers.get.side_effect = Exception("generic error")
    response = client.get("/metrics/amf")

    assert response.status_code == 200
    assert b'error' in response.content
# Test if the API handles a generic Docker error correctly.

def test_metrics_unknown_component():
    response = client.get("/metrics/unknown_service")

    assert response.status_code == 404
    assert b"Unknown component" in response.content
# Test if the API returns 404 for an unknown component.
