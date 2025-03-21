from file_transfer import FileTransfer

print("Starting Sender...")
sender = FileTransfer(5001)
print("Sending file...")
sender.send_file("test.txt", ('localhost', 6000)) 