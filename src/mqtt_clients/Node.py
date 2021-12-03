import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5
from threading import Timer

# The callback for when the client receives a CONNACK response from the server.

class Node:
    def __init__(self, client_id, services:dict={"A": 100}):
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

        #Incomming request from Client
        if msg.topic == "{}/request".format(self.client_id):
            requested_service = msg.payload.decode("utf-8") #Convert from bytes to string
            self.handle_request(requested_service=requested_service)

        #Message in an auction that the Node is hosting 
        if msg.topic in self.active_auctions_auctioning:
            message = msg.payload.decode("utf-8")
            self.handle_auction(auction_room=msg.topic, message=message, situation="auctioneer")

        #Message in an auction that the Node is participating in
        if msg.topic in self.active_auctions_bidding:
            message = msg.payload.decode("utf-8")
            self.handle_auction(auction_room=msg.topic, message=message, situation="bidder")

        #New auctions at neighbouring Nodes
        for neighbour in self.connections:
            if msg.topic == "{}/auction".format(neighbour):
                [service, room] = msg.payload.decode("utf-8").split(",")
                #Joining all auctions
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
        print("{}: Holding auction for service {} in {}.".format(self.client_id, service, self.rooms[self.room_pointer]))
        self.client.publish(
            "{}/auction".format(self.client_id), 
            "{},{}".format(service, self.rooms[self.room_pointer])
            )
        auction_room = "{}/auction/{}".format(self.client_id, self.rooms[self.room_pointer])
        self.active_auctions_auctioning[auction_room] = 0 #Setting current highest bid to zero
        self.room_pointer+=1

        #Start a thread that keeps a countdown for when the auction should be closed
        auction_timeout = Timer(interval=2, function=self.publish, kwargs={"topic":auction_room, "payload":"end"})
        auction_timeout.start()
    
    def join_auction(self, service, room, auctioneer):
        print("{}: Joining auction held by {} for {} in {}.".format(self.client_id, auctioneer, service, room))
        auction_room = "{}/auction/{}".format(auctioneer, room)
        self.client.subscribe(auction_room, qos=2)
        self.active_auctions_bidding[auction_room] = {"highest_bid":0, "service":service, "bid":0} #Setting current highest bid to zero
        self.make_bid(auction_room=auction_room, service=service)

    def make_bid(self, auction_room, service):
        bid = self.services[service]
        self.publish(auction_room, bid)
        self.active_auctions_bidding[auction_room]["bid"] = bid
        print("{}: Made a bid of {} in auction room {}".format(self.client_id, bid, auction_room))

    def handle_auction(self, auction_room, message, situation):
        if situation == "auctioneer":
            active_auctions = self.active_auctions_auctioning
        elif situation == "bidder":
            active_auctions = self.active_auctions_bidding
        else:
            print("No such situation, '{}', possible at the moment.".format(situation))
            return

        #The auction has timed out and ended
        if message == "end":
            #Remove auction from active list
            if situation == "auctioneer":
                active_auctions.pop(auction_room)
            else:
                final_standing = active_auctions.pop(auction_room)
                self.decide_winner(final_standing)
            
        #A new bid has been posted
        else:
            bid = int(message)
            if situation == "auctioneer":
                if bid > active_auctions[auction_room]:
                    active_auctions[auction_room] = bid
            elif situation == "bidder":
                if bid > active_auctions[auction_room]["highest_bid"]:
                    active_auctions[auction_room]["highest_bid"] = bid
    
    def decide_winner(self, final_standing):
        if final_standing["highest_bid"] == final_standing["bid"]:
            print("{}: I won!".format(self.client_id))
            #Do something

    #Subscribe to neighbour Node
    def add_connection(self, node_id: str):
        if node_id not in self.connections:
            self.connections.append(node_id)
            self.client.subscribe("{}/auction".format(node_id), qos=2) #Subscribe to neighbour Node's auctions
            print("{}: Connected to {}.".format(self.client_id, node_id))
        else:
            print("{}: Already Connected to {}.".format(self.client_id, node_id))

    def publish(self, topic, payload):
        self.client.publish(topic, payload, qos=2)

    def __repr__(self) -> str:
        return self.client_id

if __name__ == "__main__":
    no = Node(client_id=Node)
