from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = "http://influxdatabase:8086"
INFLUXDB_TOKEN = "t4-LvYHU3ITjvYPytZZb5nv3AJUXjKWH01izuuj01P73QujeTCJOvcxVCIMAqZAoY1lPu8oYQR26xRl0yhDNKA=="
INFLUXDB_ORG = "oai"
INFLUXDB_BUCKET = "oai_metrics"

client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()
