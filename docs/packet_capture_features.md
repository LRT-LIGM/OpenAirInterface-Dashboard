# Packet capture

## Overview

The packet capture feature of the monitoring backend allows you to capture live network traffic directly from a selected network interface using the `pyshark` library,
which is a Python wrapper over `tshark`. Captured packets are streamed to the client through a WebSocket.

## How does it work
The WebSocket route `/ws/pcap` establishes a real-time stream of captured packets using a background thread.
By default, the capture is performed on the `eth0` network interface and with no filter. Here's what happens step by step :

- The client connects to `/ws/pcap` using WebSocket, providing optional query parameters :
    - `interface`: name of the network interface to capture from (default interface is eth0 but can be changed by : any, wlan...)
    - `bpf_filter`: optional BPF filter (no filter by default but can be changed by : udp, ip...)
- A background thread starts capturing packets via `pyshark.LiveCapture`.
- Captured packets are pushed into a thread-safe Queue.
- An async FastAPI function reads from the queue and streams packets over the WebSocket.


## How to specify the interface and filter

To control which traffic is captured, provide query parameters when establishing the WebSocket connection:

```bash
ws://<your-host>/ws/pcap?interface=<interface_name>&bpf_filter=<filter_name>
```

Example usage :

```bash
ws://localhost:8001/ws/pcap?interface=any&bpf_filter=udp
```
You can visit [this website](https://www.tcpdump.org/manpages/pcap-filter.7.html) to explore all the available BPF filters and learn more about their syntax.
