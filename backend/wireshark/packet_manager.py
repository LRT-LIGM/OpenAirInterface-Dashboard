import pyshark
import threading
import asyncio
from queue import Queue
import logging
from fastapi import WebSocketException

def capture_packets_thread(interface, queue, bpf_filter):
    """
    Background packet capture using PyShark, producing detailed JSON output.

    This function captures packets from the specified network interface with
    an optional BPF filter. Each packet is parsed into a JSON dictionary
    containing IP addresses, ports, transport protocol, highest layer, and timestamp.

    Args:
        interface (str): Network interface to capture from.
        queue (Queue): Thread-safe queue to store the captured packet data.
        bpf_filter (str): Optional BPF (Berkeley Packet Filter) string.

    Returns:
        None
    """
    try:
        capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter or None)
        for packet in capture.sniff_continuously():
            try:
                summary = str(packet)
                timestamp = getattr(packet, "sniff_time", None).isoformat() if hasattr(packet, "sniff_time") else None
                highest_layer = packet.highest_layer

                ip_layer = packet.ip if hasattr(packet, 'ip') else None
                src_ip = ip_layer.src if ip_layer else None
                dst_ip = ip_layer.dst if ip_layer else None

                transport_protocol = None
                src_port = None
                dst_port = None
                if hasattr(packet, 'tcp'):
                    transport_protocol = "TCP"
                    src_port = packet.tcp.srcport
                    dst_port = packet.tcp.dstport
                elif hasattr(packet, 'udp'):
                    transport_protocol = "UDP"
                    src_port = packet.udp.srcport
                    dst_port = packet.udp.dstport

                packet_data = {
                    "summary": summary,
                    "timestamp": timestamp,
                    "ip": {
                        "src": src_ip,
                        "dst": dst_ip
                    },
                    "transport": {
                        "protocol": transport_protocol,
                        "src_port": src_port,
                        "dst_port": dst_port
                    },
                    "highest_protocol": highest_layer
                }

                queue.put(packet_data)
            except Exception as parse_error:
                queue.put({"error": f"Error parsing packet: {str(parse_error)}"})
    except Exception as e:
        queue.put({"error": f"Packet capture failed: {str(e)}"})

async def capture_packets(websocket, interface="eth0", bpf_filter=""):
    """
    Asynchronously capture and stream network packets over a WebSocket connection.

    This function launches a background thread to perform packet capture using PyShark
    on the specified network interface. Captured packets are processed into simplified
    JSON objects and streamed in real time to the WebSocket client.

    Packet data includes a summary string, capture timestamp (ISO format), packet length,
    and a list of protocol layers involved. An optional BPF (Berkeley Packet Filter) can be
    provided to filter captured packets.

    Args:
        websocket (WebSocket): The WebSocket connection used to send captured packet data.
        interface (str, optional): Network interface to capture packets from (default is 'eth0').
        bpf_filter (str, optional): Optional BPF filter to apply during packet capture.

    Returns:
        None

    Raises:
        RuntimeError: If packet capture fails or an error occurs during WebSocket communication.
    """
    packet_queue = Queue()

    try:
        logging.info("Starting packet capture")

        thread = threading.Thread(
            target=capture_packets_thread,
            args=(interface, packet_queue, bpf_filter),
            daemon=True
        )
        thread.start()

        while True:
            await asyncio.sleep(0.1)
            while not packet_queue.empty():
                packet = packet_queue.get()
                if "error" in packet:
                    await websocket.send_json(packet)
                    raise WebSocketException(code=1011)
                await websocket.send_json(packet)

    except Exception as e:
        logging.error(f"Packet capture failed: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.send_json({"error": f"Internal Server Error: {str(e)}"})
            await websocket.close(code=1011)
    finally:
        if websocket.client_state.name != "DISCONNECTED":
            logging.info("Closing WebSocket connection")
            await websocket.close()