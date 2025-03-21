import random
import socket
import time

class NetworkSimulator:
    """Simulates network problems like packet loss and corruption"""
    def __init__(self, loss_rate=0.2, corruption_rate=0.2):
        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def start(self, listen_port, forward_port):
        """Start the simulator"""
        self.socket.bind(('localhost', listen_port))
        self.forward_addr = ('localhost', forward_port)
        
        print(f"Network simulator running on port {listen_port}")
        print(f"Forwarding to port {forward_port}")
        
        while True:
            # Receive packet
            data, addr = self.socket.recvfrom(1024)
            
            # packet loss
            if random.random() < self.loss_rate:
                print("Simulating packet loss")
                continue
                
            # corruption
            if random.random() < self.corruption_rate:
                print("Simulating packet corruption")
                # Corrupt a random byte
                pos = random.randint(0, len(data) - 1)
                data = data[:pos] + bytes([random.randint(0, 255)]) + data[pos + 1:]

            time.sleep(random.uniform(0.1, 0.3))
            
            self.socket.sendto(data, self.forward_addr) 