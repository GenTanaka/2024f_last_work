import json
import socket
from datetime import datetime

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
            client.sendall(len(message).to_bytes(
                4, 'big'))  # Send length (4 bytes)
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

            # Send the length of the JSON request first
            client.sendall(len(json_request).to_bytes(
                4, 'big'))  # Send length (4 bytes)
            client.sendall(json_request)  # Send the JSON request

            # Receive the length of the response first
            length_data = client.recv(4)
            if not length_data:
                print("No length data received.")
                client.close()
                continue

            response_length = int.from_bytes(
                length_data, 'big')  # Decode the response length
            response_data = b""

            # Receive the full response data
            while len(response_data) < response_length:
                chunk = client.recv(BUFFSIZE)
                if not chunk:
                    break
                response_data += chunk

            # Decode and process the server's response
            response_json = response_data.decode('utf-8')
            response = json.loads(response_json)

            # Display the response
            if response.get("status") == "success":
                print(f"Message for {to_user}: {response.get('message')}")
            else:
                print(f"Error: {response.get('message')}")

        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            client.close()

    elif command == '3':
        print('Exiting')
        break