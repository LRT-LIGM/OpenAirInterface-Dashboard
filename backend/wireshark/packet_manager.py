from asyncio.subprocess import PIPE, create_subprocess_exec

async def capture_packets(websocket, interface="eth0", capture_filter=""):
    """
    Capture live network packets using `tshark` and stream them over a WebSocket connection.

    This function launches a subprocess running `tshark` with the given network interface
    and optional BPF filter (e.g., "udp"). The output is read line by line in JSON format
    and streamed to the connected WebSocket client.

    Args:
        websocket (WebSocket): The WebSocket connection through which packets are sent.
        interface (str, optional): The network interface to capture from. Defaults to "eth0".
        capture_filter (str, optional): An optional BPF (Berkeley Packet Filter) string
                                        to filter captured packets (e.g., "udp").

    Returns:
        None: Data is streamed continuously to the WebSocket client. The function terminates
              when the capture ends or an error occurs.

    Raises:
        None directly, but logs errors if `tshark` cannot be executed or if the WebSocket
        transmission fails.
    """

    try:
        process = await create_subprocess_exec(
            "tshark",
            "-i", interface,
            "-f", capture_filter,
            "-l",
            "-T", "json",
            stdout=PIPE,
            stderr=PIPE,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break

            try:
                decoded = line.decode("utf-8").strip()
                if decoded:
                    await websocket.send_text(decoded)
            except Exception as e:
                print(f"[ERROR] Sending line failed: {e}")
                break

    except Exception as e:
        print(f"[ERROR] Could not run tshark: {e}")
    finally:
        await websocket.close()