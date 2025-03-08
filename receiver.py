import socket
import zlib
from struct import pack, unpack

# Configuration (same as receiver.py)
HOST = '127.0.0.1'
PORT = 5000
MAX_PACKET_SIZE = 1024

class Receiver:
    # Reuse Receiver class from receiver.py with minor tweaks
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, PORT))
        self.buffer = {}
        self.expected_seq = 0

    def verify_checksum(self, packet):
        seq_num, checksum = unpack('!II', packet[:8])
        data = packet[8:]
        return zlib.crc32(data) == checksum

    def send_ack(self, seq_num, addr):
        ack = pack('!I', seq_num)
        self.sock.sendto(ack, addr)
        print(f"Sent ACK for packet {seq_num}")

    def receive(self):
        """Receive packets and return ordered data."""
        received_data = []
        while True:
            data, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
            if len(data) < 8:
                continue

            seq_num, _ = unpack('!II', data[:8])
            if self.verify_checksum(data):
                self.buffer[seq_num] = data[8:]
                self.send_ack(seq_num, addr)

                while self.expected_seq in self.buffer:
                    chunk = self.buffer[self.expected_seq]
                    if chunk == b"END":  # Check for end signal
                        return b"".join(received_data)
                    received_data.append(chunk)
                    del self.buffer[self.expected_seq]
                    self.expected_seq += 1
            else:
                print(f"Packet {seq_num} corrupted, discarding")

class Server:
    def __init__(self):
        self.receiver = Receiver()

    def receive_file(self):
        """Receive a file from the client."""
        print("Waiting for file transfer...")
        # Receive metadata first
        metadata_bytes = self.receiver.receive()
        file_name, file_size = metadata_bytes.decode().split("|")
        file_size = int(file_size)
        print(f"Receiving file: {file_name}, {file_size} bytes")

        # Receive file data
        file_data = self.receiver.receive()

        # Write file to disk
        with open(f"received_{file_name}", 'wb') as f:
            f.write(file_data)
        print(f"File saved as received_{file_name}")

if __name__ == "__main__":
    server = Server()
    server.receive_file()