import json
import socket
from datetime import datetime
import time

HOST = "bastion.jn.sfc.keio.ac.jp"  # Replace with the actual host
SEND_PORT = 13000
RECEIVE_PORT = 13001
BUFFSIZE = 4096

while True:
    command = input(
        'Press 1 if you want to send a message, 2 if you want to receive a message, 3 if you want to exit: '
    )
    if command == '1':
        sender = input('Enter your name: ')
        recipient = input('Enter the recipient\'s name: ')
        message = input('Enter the message: ')

        current_date = datetime.now()
        formatted_date = current_date.strftime('%Y/%m/%d')

        # Sending JSON data with the specified structure
        data = {
            "from": sender,
            "to": recipient,
            "message": message,
            "date": formatted_date
        }
        # Serialize the dictionary into a JSON string
        json_data = json.dumps(data)

        try:
            print('Sending message...')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, SEND_PORT))

            # Send the length of the JSON data first, then the data
            message = json_data.encode('UTF-8')
            client.sendall(message)  # Send JSON data

            print(f"Message sent: {data}")
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            client.close()

    elif command == '2':
        # Receiving JSON data
        try:
            print('Receiving message...')
            # User inputs the recipient
            to_user = input("Enter the recipient's name (to): ").strip()

            # Prepare JSON request
            request_data = {
                "to": to_user  # Only send the recipient's name
            }
            json_request = json.dumps(request_data).encode(
                'utf-8')  # Serialize the request

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, RECEIVE_PORT))

            client.sendall(json_request)  # Send the JSON request

            time.sleep(1)
            data = client.recv(BUFFSIZE)
            # Receive the response
            response_json = data.decode('UTF-8')
            response = json.loads(response_json)
            # Display the response
            print('message:', response)

        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            client.close()

    elif command == '3':
        print('Exiting')
        break