import pyshark
import threading
import asyncio
from queue import Queue

def capture_packets_thread(interface, queue, bpf_filter):
    """
    Capture packets in a separate thread using PyShark.

    This function initializes a live packet capture on the specified network interface
    and continuously places the captured packets in a thread-safe queue. An optional
    BPF (Berkeley Packet Filter) can be applied to filter the captured traffic.

    Args:
        interface (str): The name of the network interface to capture packets from (e.g., 'eth0').
        queue (Queue): A thread-safe queue to store captured packet data.
        bpf_filter (str): A BPF filter string to apply to the capture (e.g., 'udp', 'tcp port 80').

    Returns:
        None
    """
    capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter or None)
    for packet in capture.sniff_continuously():
        queue.put(str(packet))

async def capture_packets(websocket, interface="eth0", bpf_filter=""):
    """
    Asynchronously stream captured packets through a WebSocket connection.

    This function runs a background thread to capture network packets using PyShark
    and asynchronously sends the packet data to the connected WebSocket client.
    It supports optional filtering using BPF syntax.

    Args:
        websocket (WebSocket): The WebSocket connection to stream captured packet data.
        interface (str, optional): Network interface to use for capturing (default is 'eth0').
        bpf_filter (str, optional): Optional BPF filter to apply during capture.

    Returns:
        None

    Raises:
        Any exception encountered during capture or WebSocket communication is caught and logged.
    """
    packet_queue = Queue()

    try:
        thread = threading.Thread(
            target=capture_packets_thread,
            args=(interface, packet_queue, bpf_filter),
            daemon=True
        )
        thread.start()

        await websocket.send_text(f">>> STARTING PACKET CAPTURE with filter: '{bpf_filter}' <<<")
        while True:
            await asyncio.sleep(0.1)
            while not packet_queue.empty():
                packet = packet_queue.get()
                await websocket.send_text(packet)

    except Exception as e:
        print(f"[ERROR] Packet capture failed: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.send_text(f"[ERROR] Internal Server Error: {e}")
            await websocket.close(code=1011)
    finally:
        if websocket.client_state.name != "DISCONNECTED":
            print("Closing WebSocket connection")
            await websocket.close()
