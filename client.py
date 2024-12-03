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
choice = "0"
while int(choice) != 4:
    choice = input("\nChoose a query (1-3) or Cancel (4):\n"
                   "  1. What is the average moisture inside my kitchen fridge for the past 3 hours?\n"
                   "  2. What is the average water consumption per cycle in my smart dishwasher?\n"
                   "  3. Which device consumed more electricity among my three IoT devices?\n"
                   "  4. Cancel\n")
    if int(choice) == 4:
        print("Closing connection.")
        break
    elif int(choice) not in range(1, 4):
        print("Sorry, that is not a valid query choice. Please try again.\n")
        continue
    # try:
    # Send message to server and receive
    # TCPsocket.send(choice.encode())
    # print("Received from server: ", TCPsocket.recv(1024).decode())
    # TEST TODO: delete when input loop works
    print("Sending to server...")
    # except Exception as e:
    #     print("Error sending message: ", e)
    #     print()
    #     break

TCPsocket.close()