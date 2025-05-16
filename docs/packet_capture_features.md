# Packet capture

## Overview

The packet capture feature of the monitoring backend allows you to capture live network traffic directly from a selected network interface using the `pyshark` library,
which is a Python wrapper over `tshark`. Captured packets are streamed to the client through a WebSocket.

## How does it work
The WebSocket endpoint `/ws/pcap` establishes a real-time stream of captured packets using a dedicated background thread.
By default, the capture is performed on the `eth0` network interface. Here's what happens step by step :

- Client connects to /ws/pcap (optionally with a BPF filter).
- A background thread starts capturing packets via pyshark.LiveCapture.
- Captured packets are pushed into a thread-safe Queue.
- An async FastAPI function reads from the queue and streams packets over the WebSocket.


## How to change the filter

To apply a filter, use the filter query parameter when connecting to the websocket :

```bash
ws://<your-host>/ws/pcap?filter=<filter_name>
```

Example usage :

```bash
ws://localhost:8001/ws/pcap?filter=ip
```
Here is a list of the filter possible : tcp, udp, ip
You can visit [this website](https://www.tcpdump.org/manpages/pcap-filter.7.html) to explore all the available BPF filters and learn more about their syntax.

