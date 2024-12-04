from os import getenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import socket

load_dotenv()

#! vars
tcp_socket = socket.socket()
max_socket_timeouts = 30
queries = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?",
]
rejection = "Sorry, this query cannot be processed. Please try one of the following: " + ", ".join(queries)

print("starting...")

#! connect to mongodb
mongodb_uri = getenv("MONGODB_URI")

mongodb_client = MongoClient(mongodb_uri, server_api=ServerApi("1"))

try:
    mongodb_client.admin.command("ping")
    print("mongodb ping successful")
except Exception as e:
    print("mongodb ping failed", e)
    exit(1)

#! get information for the tcp server
## Keep accepting server IP address and port number until valid
while True:
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serverIP = input("enter the host ip: ")
        serverPort = int(input("enter the server port number: "))

        # Create and bind socket
        tcp_socket.bind((serverIP, serverPort))
        print("server started at port", serverPort)
        break
    except Exception as e:
        print("error encountered: ", e)
        print("please enter a valid ip address and port")

tcp_socket.listen(5)

# Keep accepting and transforming messages that are received
while True:
    client_socket, client_ip = tcp_socket.accept()
    client_socket.settimeout(1)
    socket_timeouts = 0
    print("connected to: ", client_ip)

    while True:
        try:
            received = client_socket.recv(1024)
            if received == b"":
                # If the client closes the connection, close the server connection
                print(client_ip, "closed the connection")
                break
            message = received.decode()
            if message not in queries:
                client_socket.send(rejection.encode())
                continue
            #TODO: process the query and send the result back to the client
            db = mongodb_client.get_default_database()
            if (message == queries[0]):
                print("query 1 received")
                client_socket.send("query 1".encode())
            elif (message == queries[1]):
                print("query 2 received")
                client_socket.send("query 2".encode())
            elif (message == queries[2]):
                print("query 3 received")
                client_socket.send("query 3".encode())
            else:
                print("query not found")
                client_socket.send(rejection.encode())

        except socket.timeout as e:
            # If the client is inactive for a certain amount of time, close the connection
            socket_timeouts += 1
            if socket_timeouts >= max_socket_timeouts:
                print(client_ip, "timeout")
                break
            else:
                continue
            
        except Exception as e:
            print(client_ip, "unexpected error:", e)
            break

    client_socket.close()
    print("connection closed with: ", client_ip)
    print("waiting for new connection...")
    print("listening on host: ", serverIP, ", port: ", serverPort)
