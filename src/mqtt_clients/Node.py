import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5

# The callback for when the client receives a CONNACK response from the server.

class Node:
    def __init__(self, client_id, services:dict={"A": 0, "B": 0}):
        """
            Application
        """
        self.client_id = str(client_id)
        self.services = services
        self.connections = [] #List of Node ids that should be subscribed to, i.e., Node_1
        self.rooms = ["room_{}".format(i) for i in range(10)] #Auction rooms [room_0, room_1, ...]
        self.room_pointer = 0 #Pointing to next auction room to use
        """
            Paho MQTT Client
        """
        self.client = mqtt.Client(client_id=self.client_id, protocol=MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        #print(str(rc)+ " {} connected with services {}".format(client._client_id, self.services))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.make_subscriptions()

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("{}: {} {}".format(self.client_id, msg.topic, str(msg.payload)))

        if msg.topic == "{}/request".format(self.client_id):
            requested_service = msg.payload.decode("utf-8") #Convert from bytes to string
            self.handle_request(requested_service=requested_service)
            

    def make_subscriptions(self):
        self.client.subscribe("{}/#".format(self.client_id), qos=2)

        for node in self.connections:
            self.client.subscribe("{}/auction/#".format(node), qos=2) #Subscribe to neighbour Node's auctions

    #Decide to process service or create and auction item 
    def handle_request(self, requested_service):
        #make internal bid
        #auction if below
        if requested_service in self.services:
            #print("I have the service!")
            pass
        else:
            #print("I dont have the service!")
            pass
        self.hold_auction(requested_service)

    #Create auction for item on "Node_id/auction/room_nr item_description"
    def hold_auction(self, item):
        print("{}: Holding auction for {} in {}".format(self.client_id, item, self.rooms[self.room_pointer]))
        self.client.publish("{}/auction/{}".format(self.client_id, self.rooms[self.room_pointer]), item)
        self.room_pointer+=1
    
    #Subscribe to neighbour Node
    def add_connection(self, node_id: str):
        if node_id not in self.connections:
            self.connections.append(node_id)
            self.client.subscribe("{}/auction/#".format(node_id), qos=2) #Subscribe to neighbour Node's auctions
            print("{}: Connected to {}".format(self.client_id, node_id))
        else:
            print("{}: Already Connected to {}.".format(self.client_id, node_id))

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def __repr__(self) -> str:
        return self.client_id

if __name__ == "__main__":
    no = Node(client_id=Node)
