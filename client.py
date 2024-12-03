import socket

TCPsocket = socket.socket()
# Keep accepting server IP address and port number until valid
while True:
    try:
        # Prompt user for server IP address and port
        serverIP = input("Enter the server IP adress: ")
        serverPort = int(input("Enter the server port number: "))

        # Create and connect socket
        TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPsocket.connect((serverIP, serverPort))
        print("Client: Socket successfully connected.\n")
        break
    except Exception as e:
        print("Incorrect IP address or port number: ", e)
        print()
        continue

# Keep accepting inputs until error
while True:
    message = input("Message: ")
    try:
        # Send message to server and receive
        TCPsocket.send(message.encode())
        print("Received from server: ", TCPsocket.recv(1024).decode())
    except Exception as e:
        print("Error sending message: ", e)
        print()
        break

TCPsocket.close()