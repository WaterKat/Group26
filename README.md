# Assignment 8: Build an End-to-End IoT System

### Dependencies
* MongoDB credentials
* Python 3.12.6
* [pip dependencies](./requirements.txt)

## Client
*Make sure python is installed. Make sure the server is running before attempting to run.*

Navigate to the directory where the client is located (root directory by default). Use the following command:
```
python ./client.py
```
As prompted, enter the IP address and port number of the server. 
```
Enter the server IP address: [your ip here]
Enter the server port number: [your port here]
```
Review the query choices. 
```
Choose a query (1-3) or Cancel (4):
  1. What is the average moisture inside my kitchen fridge in the past three hours?
  2. What is the average water consumption per cycle in my smart dishwasher?
  3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?
  4. Cancel
```
Enter a number 1 through 3 for any query or 4
to "Cancel" and disconnect. Send as many queries as necesssary.

## Server
### Setup
*Make sure python is installed. Ensure the pip dependencies are installed in order to run the server*

```pip install -r ./requirements.txt```

*Ensure that your port is allowed through firewalls. Both on the server machine itself, and if using a VM manager, port forward your port. ex: Allow port through Google Cloud you would allow through Firewall Policies in Network Security*

*You must also provide your credentials to your mongodb in a ```.env``` file containing the following:*
```
MONGODB_URI=mongodb+srv://{your username}:{your password}@{your uri}
```
### Running
To run the server use the following command:
```python ./server.py```
You will receive the following output:
```
starting...
```
If your credentials for mongodb are valid, you will receive:
```
mongodb ping successful
```
otherwise you will receive
```
mongodb ping failed
```
On successful connection mongodb, you will receive the prompt to enter your hosting ip and port
```
enter the host ip: [your ip here]
enter the server port number: [your port here]
```
On successful connection you will receive a final output of 
```
server started at port [your port here]
```

On successful client connections you will receive output detailing the queries made by your client. At the moment, only single clients are supported at any one time. ex:
```
connected to:  ([client ip], [client id])
sending response: The average moisture inside your kitchen fridge in the past three hours is ???
sending response: The average water consumption per cycle in your smart dishwasher is ??? gpm
([client ip], [client id]) timeout
connection closed with:  ([client ip], [client id])
waiting for new connection...
listening on host:  [client ip] , port:  [client port]
```