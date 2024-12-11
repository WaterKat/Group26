from os import getenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import socket

load_dotenv()

#! vars
tcp_socket = socket.socket()
max_socket_timeouts = 60


def LitersPerMinuteToGallonsPerMinute(lpm):
    return lpm / 3.78541


def MoistureToPercent(moisture):
    return moisture * 100


def ConvertCtoF(celsius):
    return celsius * 9 / 5 + 32


def AmpsToWatts(amps, volts, power_factor):
    return amps * volts * power_factor


def WattsToKilowattHours(watts, hours):
    return watts * hours / 1000


queries = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?",
]
rejection = (
    "Sorry, this query cannot be processed. Please try one of the following: "
    + ", ".join(queries)
)

appliance_map = {"fr-1": "fridge 1", "fr-2": "fridge 2", "dw-1": "dishwasher"}


def GetQueryOne(instanceUid, timeDifference=3):
    return [
        {
            "$project": {
                "instanceUid": "$payload.asset_uid",
                "hygrometer": "$payload.fr-1-hygrometer",
                "time": {
                    "$dateDiff": {
                        "startDate": "$time",
                        "endDate": "$$NOW",
                        "unit": "hour",
                    }
                },
            }
        },
        {
            "$match": {
                "instanceUid": instanceUid,
                "hygrometer": {"$exists": "true", "$ne": "null"},
                "time": {"$lte": timeDifference},
            }
        },
        {
            "$group": {
                "_id": "$instanceUid",
                "hygrometer": {"$avg": {"$toDouble": "$hygrometer"}},
            }
        },
    ]


def GetQueryTwo(instanceUid):
    return [
        {"$match": {"payload.asset_uid": instanceUid}},
        {
            "$group": {
                "_id": "$payload.asset_uid",
                "flow": {"$avg": {"$toDouble": "$payload.dw-1-flowmeter"}},
            }
        },
    ]

def GetQueryThree():
    return [
    {
        '$project': {
            'uid': '$payload.asset_uid', 
            'current': {
                '$switch': {
                    'branches': [
                        {
                            'case': {
                                '$eq': [
                                    '$payload.parent_asset_uid', 'fr-1'
                                ]
                            }, 
                            'then': '$payload.fr-1-ammeter'
                        }, {
                            'case': {
                                '$eq': [
                                    '$payload.parent_asset_uid', 'fr-2'
                                ]
                            }, 
                            'then': '$payload.fr-2-ammeter'
                        }, {
                            'case': {
                                '$eq': [
                                    '$payload.parent_asset_uid', 'dw-1'
                                ]
                            }, 
                            'then': '$payload.dw-1-ammeter'
                        }
                    ], 
                    'default': 'null'
                }
            }
        }
    }, {
        '$group': {
            '_id': '$uid', 
            'current': {
                '$max': '$current'
            }
        }
    }, {
        '$sort': {
            'current': -1
        }
    }
]

meta_query = [
    {
        "$unwind": {
            "path": "$customAttributes.children",
            "includeArrayIndex": "array_index",
            "preserveNullAndEmptyArrays": False,
        }
    },
    {
        "$project": {
            "assetUid": "$assetUid",
            "instanceUid": "$customAttributes.children.assetUid",
            "name": "$customAttributes.name",
        }
    },
]

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
                print("received message: ", message)
                client_socket.send(rejection.encode())
                continue
            # TODO: process the query and send the result back to the client
            data_collection = mongodb_client.get_database("dataniz").get_collection(
                "general_virtual"
            )
            metadata_collection = mongodb_client.get_database("dataniz").get_collection(
                "general_metadata"
            )
            devices = list(metadata_collection.aggregate(meta_query))
            if message == queries[0]:
                possible_device = next(
                    (i for i in devices if i["assetUid"] == "fr-1"), None
                )
                if possible_device == None:
                    response_string = "No device found"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                fridge_uid = possible_device["instanceUid"]
                aggr_result = data_collection.aggregate(GetQueryOne(fridge_uid))
                aggr_list = list(aggr_result)
                if len(aggr_list) == 0:
                    response_string = "No data found in the past three hours"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                reading = aggr_list[0]["hygrometer"] / 100
                moisture_percentage = MoistureToPercent(reading)
                if moisture_percentage is None:
                    moisture_percentage = 0
                if moisture_percentage < 0:
                    moisture_percentage = 0
                if moisture_percentage > 100:
                    moisture_percentage = 100
                response_string = f"The average moisture inside your kitchen fridge {possible_device["name"]} in the past three hours is {int(moisture_percentage)}%"
                print(f"sending response: {response_string}")
                client_socket.send(response_string.encode())
            elif message == queries[1]:
                possible_device = next(
                    (i for i in devices if i["assetUid"] == "dw-1"), None
                )
                if possible_device == None:
                    response_string = "No device found"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                instanceUid = possible_device["instanceUid"]
                aggr_result = data_collection.aggregate(GetQueryTwo(instanceUid))
                aggr_list = list(aggr_result)
                if len(aggr_list) == 0:
                    response_string = "No data found"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                moisture_percentage = aggr_list[0]["flow"]
                cycle_hours = 2
                gpm = LitersPerMinuteToGallonsPerMinute(moisture_percentage)
                response_string = f"The average water consumption per cycle in your smart dishwasher {possible_device["name"]} is {moisture_percentage:.1f} gpm"
                print(f"sending response: {response_string}")
                client_socket.send(response_string.encode())
            elif message == queries[2]:
                aggr_result = data_collection.aggregate(GetQueryThree())
                aggr_list = list(aggr_result)
                if len(aggr_list) == 0:
                    response_string = "No data found"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                instanceUid = aggr_list[0]["_id"]
                amps = float(aggr_list[0]["current"])
                watts = AmpsToWatts(amps, 120, 1)
                wHours = WattsToKilowattHours(watts, 1.5)
                matchingDevice = next((i for i in devices if i["instanceUid"] == instanceUid), None)
                if matchingDevice is None:
                    response_string = "No device found"
                    print(f"sending response: {response_string}")
                    client_socket.send(response_string.encode())
                    continue
                response_string = f"The device that consumed more electricity among your three IoT devices is {matchingDevice["name"]} with {wHours:.1f} kWh"
                print(f"sending response: {response_string}")
                client_socket.send(response_string.encode())
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
