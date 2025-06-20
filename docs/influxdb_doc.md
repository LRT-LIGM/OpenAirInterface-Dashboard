# InfluxDB Integration

## Starting InfluxDB

To start InfluxDB, use the following command from the root of the project :

```bash
docker compose up --build
```
Once the container is running, you can access the InfluxDB web interface at :  
`http://localhost:8086/signin`

By default, if you haven't changed the config, you can log in using :

Username : `admin`  
Password : `admin123`

You can change the default username and password in the `docker-compose.yaml` file under the environment section of the influxdb service.

---

## Testing InfluxDB Integration

To test the InfluxDB setup, run a script that pushes fake CPU and RAM usage data. From the project root, use :

```bash
PYTHONPATH=. python3 tests/influxdb_example_command.py
```
This script will send CPU and RAM metrics to InfluxDB every 2 seconds.

---

## Visualizing the Data in InfluxDB

-  Go to the InfluxDB web interface: http://localhost:8086

- Navigate to Data Explorer (in the left-hand menu)

- Select the oai_metrics bucket

- Choose the system_usage measurement

- Add fields such as cpu or ram to generate the graph

You should now see a live chart of your pushed metrics.

---

## Viewing Metrics via WebSocket

You can also view real-time metrics via WebSocket by connecting to :

- CPU usage : `ws://localhost:8001/ws/metrics?metric_name=cpu&ue_id=UE_001`

- RAM usage : `ws://localhost:8001/ws/metrics?metric_name=ram&ue_id=UE_001`

These endpoints will stream the latest values based on the metrics stored in InfluxDB.


