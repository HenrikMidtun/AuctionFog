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
        self.active_auctions_bidding = {} #Topics where the Node is currently participating in an auction including largest current bid, e.g., {Node_0/auctions/room_2: 48}
        self.active_auctions_auctioning = {} #Topics where the Node is currently acting as an auctioneer including largest current bid

        """
            Paho MQTT Client
        """
        self.client = mqtt.Client(client_id=self.client_id, protocol=MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    """
        Callbacks
    """
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

        if msg.topic in self.active_auctions_auctioning:
            message = msg.payload.decode("utf-8")
            if message == "end":
                #Remove auction from active list
                pass
            else:
                bid = message
                self.active_auctions_auctioning[msg.topic] = int(bid)

        if msg.topic in self.active_auctions_bidding:
            message = msg.payload.decode("utf-8")
            if message == "end":
                #Remove auction from active list and decide winner
                pass
            else:
                bid = message
                self.active_auctions_bidding[msg.topic] = int(bid)

        for neighbour in self.connections:
            if msg.topic == "{}/auction".format(neighbour):
                [service, room] = msg.payload.decode("utf-8").split(",")
                self.join_auction(service=service, room=room, auctioneer=neighbour)
        
    """
        Node Methods
    """
    def make_subscriptions(self):
        self.client.subscribe("{}/#".format(self.client_id), qos=2)

        for node in self.connections:
            self.client.subscribe("{}/auction".format(node), qos=2) #Subscribe to neighbour Node's auctions

    #Decide to process service or create and auction item 
    def handle_request(self, requested_service):
        #make internal bid
        #auction if below
        if requested_service in self.services:
            if self.services[requested_service] < 200: #Checking against asking price, Set realistically later!
                self.hold_auction(requested_service)
            else:
                #process service
                pass
        else:
            self.hold_auction(requested_service)
            
    #Create auction for item on "Node_id/auction/room_nr item_description"
    def hold_auction(self, service):
        print("{}: Holding auction for {} in {}.".format(self.client_id, service, self.rooms[self.room_pointer]))
        self.client.publish(
            "{}/auction".format(self.client_id), 
            "{},{}".format(service, self.rooms[self.room_pointer])
            )
        self.active_auctions_auctioning["{}/auction/{}".format(self.client_id, self.rooms[self.room_pointer])] = 0 #Setting current highest bid to zero
        self.room_pointer+=1
    
    def join_auction(self, service, room, auctioneer):
        print("{}: Joining auction held by {} for {} in {}.".format(self.client_id, auctioneer, service, room))
        auction_room = "{}/auction/{}".format(auctioneer, room)
        self.client.subscribe(auction_room, qos=2)
        self.active_auctions_bidding[auction_room] = 0 #Setting current highest bid to zero
        self.publish(auction_room, self.services[service])
    
    #Subscribe to neighbour Node
    def add_connection(self, node_id: str):
        if node_id not in self.connections:
            self.connections.append(node_id)
            self.client.subscribe("{}/auction".format(node_id), qos=2) #Subscribe to neighbour Node's auctions
            print("{}: Connected to {}.".format(self.client_id, node_id))
        else:
            print("{}: Already Connected to {}.".format(self.client_id, node_id))

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def __repr__(self) -> str:
        return self.client_id

if __name__ == "__main__":
    no = Node(client_id=Node)
