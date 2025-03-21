from simple_protocol import DataTransferProtocol

class FileTransfer:
    """Simple file transfer using our reliable protocol"""
    def __init__(self, port):
        self.protocol = DataTransferProtocol()
        self.protocol.socket.bind(('localhost', port))
        
    def send_file(self, filename, dest_address):
        """Send a file to destination"""
        try:
            with open(filename, 'r') as file:
                data = file.read()
                print(f"Sending file {filename}")
                success = self.protocol.send_with_ack(data, dest_address)
                if not success:
                    print("Warning: No acknowledgment received, but file may have been transferred")
        except FileNotFoundError:
            print(f"File {filename} not found")
    
    def receive_file(self, output_filename):
        """Receive a file and save it"""
        print("Waiting to receive file...")
        data = self.protocol.receive_and_ack()
        
        with open(output_filename, 'w') as file:
            file.write(data)
        print(f"File saved as {output_filename}") 