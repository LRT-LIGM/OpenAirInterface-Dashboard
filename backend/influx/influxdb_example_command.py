import psutil
import time
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influx_config import INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN

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
        mem_percent = psutil.virtual_memory().percent

        point_cpu = (
            Point("system_usage")
            .field("cpu", cpu_percent)
            .tag("ue_id", "UE_001")
            .tag("metric_name", "cpu")
        )

        point_mem = (
            Point("system_usage")
            .field("memory", mem_percent)
            .tag("ue_id", "UE_001")
            .tag("metric_name", "memory")
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=[point_cpu, point_mem])
        print(f"[PUSH] CPU={cpu_percent}%, MEM={mem_percent}%")

        time.sleep(2)


if __name__ == "__main__":
    push_fake_metrics_loop()

#start with : python3 influxdb_example_command.py
#and connect to the websocket at :
        # ws://localhost:8001/ws/metrics?metric_name=cpu&ue_id=UE_001
        # or
        # ws://localhost:8001/ws/metrics?metric_name=memory&ue_id=UE_001

