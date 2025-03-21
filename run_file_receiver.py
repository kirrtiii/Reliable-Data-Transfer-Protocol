from file_transfer import FileTransfer

print("Starting Receiver...")
receiver = FileTransfer(5000)
print("Waiting for file...")
receiver.receive_file("received_file.txt") 