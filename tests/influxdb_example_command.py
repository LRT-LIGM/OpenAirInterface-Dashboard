import psutil
import time
from influxdb_client import InfluxDBClient, Point, WriteOptions
from backend.influx.influx_config import INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN

INFLUXDB_URL = "http://localhost:8086"

client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

write_api = client.write_api(write_options=WriteOptions(batch_size=1))


#push the memory and the cpu usage for testing InfluxDB
def push_fake_metrics_loop():
    while True:
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent

        point_cpu = (
            Point("system_usage")
            .field("cpu", cpu_percent)
            .tag("ue_id", "UE_001")
            .tag("metric_name", "cpu")
        )

        point_ram = (
            Point("system_usage")
            .field("ram", ram_percent)
            .tag("ue_id", "UE_001")
            .tag("metric_name", "ram")
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point_cpu, point_ram])
        print(f"[PUSH] CPU={cpu_percent}%, MEM={ram_percent}%")

        time.sleep(2)


if __name__ == "__main__":
    push_fake_metrics_loop()

#start with : PYTHONPATH=. python3 tests/influxdb_example_command.py

#and connect to the websocket at :
        # ws://localhost:8001/ws/metrics?metric_name=cpu&ue_id=UE_001
        # or
        # ws://localhost:8001/ws/metrics?metric_name=ram&ue_id=UE_001

