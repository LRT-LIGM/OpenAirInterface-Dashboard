from asyncio.subprocess import PIPE, create_subprocess_exec

async def capture_packets(websocket, interface="eth0", capture_filter=""):
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