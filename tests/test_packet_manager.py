import pytest
import asyncio
from unittest.mock import patch, MagicMock
from backend.wireshark.packet_manager import capture_packets


class MockWebSocket:
    def __init__(self):
        self.sent_messages = []

    async def send_text(self, message):
        self.sent_messages.append(message)

    async def close(self):
        self.sent_messages.append("WebSocket closed")


@pytest.mark.asyncio
async def test_capture_packets_sends_mocked_packets():
    mock_ws = MockWebSocket()

    # Mock sniff_continuously to yield 3 fake packets
    mock_capture = MagicMock()
    mock_capture.sniff_continuously.return_value = ["Fake Packet 1", "Fake Packet 2", "Fake Packet 3"]

    with patch("backend.wireshark.packet_manager.pyshark.LiveCapture", return_value=mock_capture):
        task = asyncio.create_task(capture_packets(mock_ws, interface="eth0", bpf_filter=""))

        # Wait for some packets to be sent
        await asyncio.sleep(0.5)

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    # Checks that the packets were sent via simulated websocket
    assert any("STARTING PACKET CAPTURE" in msg for msg in mock_ws.sent_messages)
    assert "Fake Packet 1" in mock_ws.sent_messages
    assert "Fake Packet 2" in mock_ws.sent_messages
    assert "Fake Packet 3" in mock_ws.sent_messages
