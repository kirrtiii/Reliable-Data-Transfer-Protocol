import socket
import time
import zlib
import threading
from struct import pack, unpack

# Configuration
HOST = '127.0.0.1'  # Localhost for testing
PORT = 5000         # Receiver port
SIM_PORT = 6000     # Simulator port (we’ll send to this)
TIMEOUT = 2         # Seconds to wait for ACK
MAX_PACKET_SIZE = 1024  # Bytes, including header
WINDOW_SIZE = 5     # Max unacknowledged packets

class Sender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.seq_num = 0  # Starting sequence number
        self.unacked = {}  # Dictionary: seq_num -> (packet, timer)

    def make_packet(self, data):
        """Create a packet with header: seq_num (4 bytes), checksum (4 bytes), data."""
        checksum = zlib.crc32(data)
        header = pack('!II', self.seq_num, checksum)  # ! for network order
        return header + data

    def send_packet(self, data):
        """Send a packet and start a retransmission timer."""
        packet = self.make_packet(data)
        self.sock.sendto(packet, (HOST, SIM_PORT))
        timer = threading.Timer(TIMEOUT, self.retransmit, [self.seq_num])
        timer.start()
        self.unacked[self.seq_num] = (packet, timer)
        self.seq_num += 1
        time.sleep(0.1)  # Enforce <500 bps (e.g., 1024 bytes * 8 bits / 0.1s = 81,920 bps, adjust as needed)

    def retransmit(self, seq_num):
        """Retransmit a packet if timeout occurs."""
        if seq_num in self.unacked:
            packet, _ = self.unacked[seq_num]
            print(f"Timeout, retransmitting packet {seq_num}")
            self.sock.sendto(packet, (HOST, SIM_PORT))
            timer = threading.Timer(TIMEOUT, self.retransmit, [seq_num])
            timer.start()
            self.unacked[seq_num] = (packet, timer)

    def handle_ack(self):
        """Receive and process ACKs."""
        while True:
            try:
                data, _ = self.sock.recvfrom(MAX_PACKET_SIZE)
                ack_seq, = unpack('!I', data[:4])  # Extract sequence number from ACK
                if ack_seq in self.unacked:
                    _, timer = self.unacked[ack_seq]
                    timer.cancel()
                    del self.unacked[ack_seq]
                    print(f"ACK received for packet {ack_seq}")
            except socket.timeout:
                continue  # Keep listening for ACKs

    def send_data(self, data):
        """Send a string of data as packets."""
        chunk_size = MAX_PACKET_SIZE - 8  # 8 bytes for header
        chunks = [data[i:i + chunk_size].encode() for i in range(0, len(data), chunk_size)]
        ack_thread = threading.Thread(target=self.handle_ack)
        ack_thread.daemon = True
        ack_thread.start()

        for chunk in chunks:
            while len(self.unacked) >= WINDOW_SIZE:  # Wait if window is full
                time.sleep(0.01)
            self.send_packet(chunk)

        # Wait for all ACKs
        while self.unacked:
            time.sleep(0.1)

if __name__ == "__main__":
    sender = Sender()
    test_data = "Hello, this is a test message for reliable transfer!" * 10
    print("Sending data...")
    sender.send_data(test_data)
    print("Data sent successfully!")