import socket
import struct
import hashlib
import time

class Packet:
    """
    A class representing a packet in the reliable transfer protocol.

    Attributes:
        seq_num (int): Sequence number of the packet
        data (str): Data content of the packet
        checksum (str): MD5 checksum for data integrity
    """
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self):
        """
        Calculate MD5 checksum of packet contents.

        Returns:
            str: Hexadecimal string of MD5 checksum
        """
        content = str(self.seq_num) + str(self.data)
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_valid(self):
        """
        Verify packet integrity using checksum.

        Returns:
            bool: True if packet is valid, False if corrupted
        """
        return self.checksum == self._calculate_checksum()

    def to_bytes(self):
        """
        Convert packet to bytes for transmission.

        Returns:
            bytes: Packet data in bytes format
        """
        header = struct.pack('!I', self.seq_num) + self.checksum.encode()
        return header + self.data.encode()

    @classmethod
    def from_bytes(cls, byte_data):
        """
        Create packet from received bytes.

        Args:
            byte_data (bytes): Received packet data

        Returns:
            Packet: New packet instance
        """
        seq_num = struct.unpack('!I', byte_data[:4])[0]
        checksum = byte_data[4:36].decode()
        data = byte_data[36:].decode()
        packet = cls(seq_num, data)
        packet.checksum = checksum
        return packet

class DataTransferProtocol:
    """
    Implementation of reliable data transfer protocol.

    Attributes:
        timeout (float): Timeout duration for packet acknowledgment
        socket (socket): UDP socket for communication
    """
    def __init__(self, timeout=2.0):
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send_with_ack(self, data, address):
        """
        Send data with acknowledgment mechanism.

        Args:
            data (str): Data to send
            address (tuple): Destination address (host, port)

        Returns:
            bool: True if transfer confirmed successful, False otherwise
        """
        packet = Packet(1, data)
        max_retries = 5
        success = False
        
        for attempt in range(max_retries):
            try:
                self.socket.sendto(packet.to_bytes(), address)
                print(f"Sent packet, attempt {attempt + 1}")
                
                try:
                    self.socket.settimeout(self.timeout)
                    ack_data, _ = self.socket.recvfrom(1024)
                    ack_packet = Packet.from_bytes(ack_data)
                    
                    if ack_packet.is_valid() and ack_packet.data == "ACK":
                        print("Received valid ACK")
                        print("Data sent successfully!")
                        success = True
                        break
                    
                except socket.timeout:
                    print(f"Timeout occurred, retrying...")
                    continue
                except ConnectionResetError:
                    print(f"Connection reset, retrying...")
                    time.sleep(1)
                    continue
                
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(1)
                continue
        
        if not success:
            print("Note: Transfer may have succeeded even without acknowledgment")
        return success

    def receive_and_ack(self):
        """
        Receive data and send acknowledgment.

        Returns:
            str: Received data if valid
        """
        max_ack_attempts = 3
        while True:
            try:
                data, address = self.socket.recvfrom(1024)
                packet = Packet.from_bytes(data)
                
                if packet.is_valid():
                    print("Received valid packet")
                    ack_packet = Packet(1, "ACK")
                    for _ in range(max_ack_attempts):
                        try:
                            self.socket.sendto(ack_packet.to_bytes(), address)
                            print("Sent ACK")
                        except:
                            continue
                    return packet.data
                else:
                    print("Received corrupted packet")
            except Exception as e:
                print(f"Error in receive_and_ack: {e}")
                continue 