import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5
from threading import Timer
from Configuration import Catalogue, AuctionConfig, ProcessingConfig
from RequestMonitor import RequestMonitor

class AuctionNode:
    def __init__(self, client_id, request_monitor: RequestMonitor, services:dict={"A": 100}):
        """
            Application
        """
        self.client_id = str(client_id)
        self.request_monitor = request_monitor
        self.services = services
        self.connections = [] #List of Node ids that should be subscribed to, i.e., Node_1
        self.rooms = ["room_{}".format(i) for i in range(100)] #Auction rooms [room_0, room_1, ...]
        self.room_pointer = 0 #Pointing to next auction room to use
        self.active_auctions_bidding = {} #Topics where the Node is currently participating in an auction including largest current bid,this Node's bid, and amount of bids, e.g., {Node_0/auctions/room_2: {"highest_bid":48, "bid":36, "n_bids":2}}
        self.active_auctions_auctioning = {} #Topics where the Node is currently acting as an auctioneer including largest current bid and this Node's bid, and amount of bids.
        self.auction_period = AuctionConfig.auction_period #Duration from start signal of auction until end signal
        self.joining_period = AuctionConfig.joining_period #Duration from publication of auction until start signal
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
        print(str(rc)+ " {} connected with services {}".format(client._client_id, self.services))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.make_subscriptions()

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("{}: {} {}".format(self.client_id, msg.topic, str(msg.payload)))

        #Incomming request from Client
        if msg.topic == "{}/request".format(self.client_id):
            [request_id, requested_service] = msg.payload.decode("utf-8").split(",") #Convert from bytes to string
            self.handle_item(service=requested_service, request_id=request_id)

        #Message in an auction that the Node is hosting 
        if msg.topic in self.active_auctions_auctioning:
            message = msg.payload.decode("utf-8")
            self.handle_auction(auction_room=msg.topic, message=message, situation="auctioneer")

        #Message in an auction that the Node is participating in
        if msg.topic in self.active_auctions_bidding:
            message = msg.payload.decode("utf-8")
            self.handle_auction(auction_room=msg.topic, message=message, situation="bidder")

        #Node has initiated an auction
        if msg.topic == "{}/auction".format(self.client_id):
            [request_id, service, room_id] = msg.payload.decode("utf-8").split(",")
            self.start_auction(room_id=room_id)

        #New auctions at neighbouring Nodes
        for neighbour in self.connections:
            if msg.topic == "{}/auction".format(neighbour):
                [request_id, service, room] = msg.payload.decode("utf-8").split(",")
                #Joining all auctions
                self.join_auction(request_id=request_id, service=service, room=room, auctioneer=neighbour) 
        
    """
        Node Methods
    """
    def make_subscriptions(self):
        self.client.subscribe("{}/#".format(self.client_id), qos=2)

        for node in self.connections:
            self.client.subscribe("{}/auction".format(node), qos=2) #Subscribe to neighbour Node's auctions

    #Decide to process service or auction item 
    def handle_item(self, service, request_id):
        if service in self.services:
            if self.services[service] < Catalogue.services[service]["asking_price"]: #Checking against asking price
                self.initiate_auction(service=service, request_id=request_id)
            else:
                self.process_service(service=service, request_id=request_id)
        else:
            self.initiate_auction(service=service, request_id=request_id)
    
    #Calculates processing time and "processes" service in its own thread
    def process_service(self, service, request_id):
        self.request_monitor.start_processing(request_id=int(request_id), node_id=self.client_id)
        bid = self.services[service]
        std_processing_duration = Catalogue.services[service]["std_process_t"]
        process_duration = std_processing_duration*(1+ProcessingConfig.processing_constant*(50-bid)/50)
        t_service_process = Timer(interval=process_duration, function=self.request_monitor.complete_processing, kwargs={"request_id":int(request_id), "node_id":self.client_id})
        t_service_process.setDaemon(True)
        t_service_process.start()
            
    #Direct neighbours to auction for item on "Node_id/auction/room_nr"
    def initiate_auction(self, service, request_id):
        print("{}: Holding auction for request {} of service {} in {}.".format(self.client_id, request_id, service, self.rooms[self.room_pointer]))
        self.client.publish(
            "{}/auction".format(self.client_id), 
            "{},{},{}".format(request_id, service, self.rooms[self.room_pointer])
            )
        auction_room = "{}/auction/{}".format(self.client_id, self.rooms[self.room_pointer])
        self.active_auctions_auctioning[auction_room] = {"highest_bid":0, "service":service, "n_bids":0, "bid":0, "request_id": request_id} #Setting current highest bid to zero
        self.increment_room_pointer()

    def start_auction(self, room_id):
        auction_room = "{}/auction/{}".format(self.client_id, room_id)
        #A thread that keeps a countdown for when the auction should start
        t_auction_start = Timer(interval=self.joining_period, function=self.publish, kwargs={"topic":auction_room, "payload":"start"})
        t_auction_start.setDaemon(True)
        t_auction_start.start()

    def increment_room_pointer(self):
        self.room_pointer += 1
        if self.room_pointer == len(self.rooms):
            self.room_pointer = 0
    
    #Node joins an auction by subscribing to auctioneers auction topic
    def join_auction(self, request_id, service, room, auctioneer):
        print("{}: Joining auction on request {} held by {} for {} in {}.".format(self.client_id, request_id, auctioneer, service, room))
        auction_room = "{}/auction/{}".format(auctioneer, room)
        self.client.subscribe(auction_room, qos=2)
        self.active_auctions_bidding[auction_room] = {"highest_bid":0, "service":service, "n_bids":0, "bid":0, "request_id": request_id} #Setting current highest bid to zero

    #The message handler for active auctions
    def handle_auction(self, auction_room, message, situation):
        if situation == "auctioneer":
            active_auctions = self.active_auctions_auctioning
        elif situation == "bidder":
            active_auctions = self.active_auctions_bidding
        else:
            print("No such situation, '{}', possible at the moment.".format(situation))
            return

        #The auction has ended
        if message == "end":
            final_standing = active_auctions.pop(auction_room)
            if situation == "auctioneer":
                if final_standing["n_bids"] == 1: #If the only bid is from the auctioneer
                    self.process_service(service=final_standing["service"], request_id=final_standing["request_id"])
                if self.decide_winner(final_standing=final_standing): #If the auctioneer wins the auction it should process the service and not auction it
                        self.process_service(service=final_standing["service"], request_id=final_standing["request_id"])
            #Winning bidders can choose if they will re-auction the item or process it.
            elif situation == "bidder":
                if self.decide_winner(final_standing=final_standing):
                    self.handle_item(service=final_standing["service"], request_id=final_standing["request_id"])
                self.client.unsubscribe(auction_room)
        
        #The auction has begun and the bidding can start
        elif message == "start":
            service = active_auctions[auction_room]["service"]
            bid = self.make_bid(auction_room=auction_room, service=service)
            active_auctions[auction_room]["bid"] = bid

            if situation == "auctioneer":
                #A thread that keeps a countdown for when the auction should be closed
                t_auction_timeout = Timer(interval=self.joining_period+self.auction_period, function=self.publish, kwargs={"topic":auction_room, "payload":"end"})
                t_auction_timeout.setDaemon(True)
                t_auction_timeout.start()

        #A new bid has been posted
        else:
            active_auctions[auction_room]["n_bids"] = active_auctions[auction_room]["n_bids"]+1
            bid = int(message)
            if bid > active_auctions[auction_room]["highest_bid"]:
                    active_auctions[auction_room]["highest_bid"] = bid

    #The Node checks if it has won an auction and responds accordingly
    def decide_winner(self, final_standing):
        return final_standing["highest_bid"] == final_standing["bid"]

    #Decides the appropriate bid size, publishes bid and returns bid
    def make_bid(self, auction_room, service):
        bid = self.services[service]
        if service in self.services:
            bid = self.services[service]
        else:
            bid = 0
        self.publish(auction_room, bid)
        print("{}: Made a bid of {} in auction room {}.".format(self.client_id, bid, auction_room))
        return bid

    #Subscribe to neighbour Node
    def add_connection(self, node_id: str):
        if node_id not in self.connections:
            self.connections.append(node_id)
            self.client.subscribe("{}/auction".format(node_id), qos=2) #Subscribe to neighbour Node's auctions
            #print("{}: Connected to {}.".format(self.client_id, node_id))
        else:
            #print("{}: Already Connected to {}.".format(self.client_id, node_id))
            pass
    #QoS level 2 publish method
    def publish(self, topic, payload):
        self.client.publish(topic, payload, qos=2)
    
    def update_services(self, new_services):
        print("{}: Services updated to {}.".format(self.client_id, new_services))
        self.services = new_services

    def __repr__(self) -> str:
        return self.client_id

