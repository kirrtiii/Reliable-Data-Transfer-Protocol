from data_transfer import DataTransfer

print("Starting Data Receiver...")
receiver = DataTransfer(5000)
print("Waiting for messages...")

while True:
    try:
        received_message = receiver.receive_data()
    except KeyboardInterrupt:
        print("\nStopping receiver...")
        break 