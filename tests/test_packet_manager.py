import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.wireshark.packet_manager import capture_packets


class MockClientState:
    def __init__(self, name="CONNECTED"):
        self.name = name

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.client_state = MockClientState()

    async def send_json(self, message):
        self.sent_messages.append(message)

    async def close(self, code=None):
        self.sent_messages.append(f"WebSocket closed with code {code}")


class FakeLayer:
    def __init__(self, name):
        self.layer_name = name

class FakePacket:
    def __init__(self, summary, sniff_time, length, layers):
        self._summary = summary
        self.sniff_time = sniff_time
        self.length = length
        self.layers = [FakeLayer(name) for name in layers]

    def __str__(self):
        return self._summary


@pytest.mark.asyncio
async def test_capture_packets_sends_mocked_packets():
    mock_ws = MockWebSocket()

    fake_packets = [
        FakePacket("Fake Packet 1", datetime.now(), 100, ["eth", "ip"]),
        FakePacket("Fake Packet 2", datetime.now(), 150, ["eth", "ip", "tcp"]),
        FakePacket("Fake Packet 3", datetime.now(), 200, ["eth", "ip", "udp"]),
    ]

    async def fake_sniff_continuously():
        for pkt in fake_packets:
            yield pkt

    # sniff_continuously is not an async generator in pyshark
    # So we just simulate a simple iterator
    def fake_sniff_continuously_sync():
        for pkt in fake_packets:
            yield pkt

    mock_capture = MagicMock()
    mock_capture.sniff_continuously = fake_sniff_continuously_sync

    with patch("backend.wireshark.packet_manager.pyshark.LiveCapture", return_value=mock_capture):
        task = asyncio.create_task(capture_packets(mock_ws, interface="eth0", bpf_filter=""))

        await asyncio.sleep(0.5)

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    # Verify that the packets are properly sent
    sent_summaries = [msg.get("summary") for msg in mock_ws.sent_messages if isinstance(msg, dict)]

    assert "Fake Packet 1" in sent_summaries
    assert "Fake Packet 2" in sent_summaries
    assert "Fake Packet 3" in sent_summaries