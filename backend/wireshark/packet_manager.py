import pyshark
import threading
import asyncio
from queue import Queue
import logging
from fastapi import WebSocketException

def capture_packets_thread(interface, queue, bpf_filter):
    """
    Background packet capture using PyShark, producing simplified JSON output.

    This function runs in a separate thread, capturing packets from the specified
    network interface with an optional BPF filter. Each packet is parsed into a
    JSON-serializable dictionary containing a summary, timestamp, length, and
    protocol layers, then placed into a thread-safe queue.

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
            packet_data = {
                "summary": str(packet),
                "timestamp": getattr(packet, "sniff_time", None).isoformat() if hasattr(packet, "sniff_time") else None,
            }
            queue.put(packet_data)
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