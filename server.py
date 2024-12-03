from os import getenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import socket

TCPsocket = socket.socket()

# Keep accepting server IP address and port number until valid
while True:
    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Prompt user for server IP address and server port
        serverIP = input("Enter the host: ")
        serverPort = int(input("Enter the server port number: "))

        # Create and bind socket
        TCPsocket.bind((serverIP, serverPort))
        print("Server started at port", serverPort)
        break
    except Exception as e:
        print("Incorrect IP or port number: ", e)

TCPsocket.listen(5)

# Keep accepting and transforming messages that are received
while True:
    incomingSock, incomingAddr = TCPsocket.accept()
    print("Connected to ", incomingAddr)
    while True:
        try:
            # Get the received message
            message = str(incomingSock.recv(1024).decode())
            if not message:
                break
        except Exception as e:
            print(incomingAddr,"error:", e)
            incomingSock.close()
            break
        print(incomingAddr, " < ", message)
        # Transform the message
        message = message.upper()
        print(incomingAddr, " > ", message)
        # Send the tranformed message back to the client
        incomingSock.send(message.encode())