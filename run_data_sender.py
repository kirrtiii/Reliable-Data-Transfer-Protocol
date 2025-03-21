from data_transfer import DataTransfer

print("Starting Data Sender...")
sender = DataTransfer(5001)

while True:
    message = input("Enter message to send (or 'quit' to exit): ")
    if message.lower() == 'quit':
        break
    print("Sending message...")
    sender.send_data(message, ('localhost', 6000)) 