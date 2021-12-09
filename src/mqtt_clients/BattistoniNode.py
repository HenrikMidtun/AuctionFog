from platform import node
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5
from threading import Timer
from Configuration import Catalogue, ProcessingConfig
from RequestMonitor import RequestMonitor
import copy


"""
    The Node based on the task assignment system proposed by Battistoni.
    In this network all participating and able Nodes will start to process an incoming request of a service.
    The processing for all Nodes will end as soon as a Node has completed the service.

    Battistoni uses broker bridging to connect multiple brokers.
    However the demonstration relies on a single broker.
    Therefore, the Nodes are propagated over topics and subscriptions to lowest topic level emulate connecting to a broker.

    Assumptions for Battistoni Node:
        
"""
class BattistoniNode:
    def __init__(self, client_id, request_monitor: RequestMonitor, services:dict={"A": 100}):
        """
            Application
        """
        self.client_id = str(client_id)
        self.request_monitor = request_monitor
        self.services = services
        self.connections = []
        self.rooms = ["room_{}".format(i) for i in range(100)] #Auction rooms [room_0, room_1, ...]
        self.room_pointer = 0 #Pointing to next auction room to use
        self.active_processes = {} #Keeps the threads of the processes
        self.active_rooms = {} #Keeps the topic of rooms on oneself and also parent room
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
        self.make_subscriptions()

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("{}: {} {}".format(self.client_id, msg.topic, str(msg.payload)))

        #Incomming request from Client, propagate, subscribe and start processing
        if msg.topic == "{}/request".format(self.client_id):
            [request_id, service] = msg.payload.decode("utf-8").split(",") #Convert from bytes to string
            room_id = self.rooms[self.room_pointer]
            self.increment_room_pointer()
            request_room_topic = self.propagate_request(service=service, request_id=request_id, room_id=room_id, parent_id=None) #publishes onto self.client_id/X req_id, room_id
            self.handle_item(service=service, request_id=request_id, room_topic=request_room_topic)
        
        #Incomming new request from Node, subscribe, propagate and start processing 
        for node_id in self.connections:
            for service in self.services:
                if msg.topic == "{}/{}".format(node_id, service):
                    [request_id, room_id] = msg.payload.decode("utf-8").split(",") #Convert from bytes to string
                    request_room_topic = self.propagate_request(service=service, request_id=request_id, room_id=room_id, parent_id=node_id)
                    self.handle_item(service=service, request_id=request_id, room_topic=request_room_topic)

        #End signal in one of the active rooms on oneself. Unsubscribe and abort process if still active
        currently_active_rooms = copy.copy(self.active_rooms)
        for room in currently_active_rooms:
            if msg.topic == room and msg.payload.decode("utf-8") == "end":
                if room in self.active_processes:
                    process = self.active_processes.pop(room)
                    [t_process, request_id] = [process["t_process"], process["request_id"]]
                    self.abort_processing(t_process=t_process, request_id=request_id)
                self.client.unsubscribe(room)
                parent_room = self.active_rooms.pop(room)
                if parent_room != None:
                    self.client.unsubscribe(parent_room)
                    self.client.publish(parent_room, "end")
        
        #End signal in parent room
        currently_active_rooms = copy.copy(self.active_rooms)
        for room, parent_room in currently_active_rooms.items():
            if msg.topic == parent_room and msg.payload.decode("utf-8") == "end":
                self.client.publish(room, "end")
    """
        Node Methods
    """
    def make_subscriptions(self):
        self.client.subscribe("{}/request".format(self.client_id), qos=2)
        for service in self.services:
            for node_id in self.connections:
                self.client.subscribe("{}/{}".format(node_id, service), qos=2)

    #Connect to a node as a neighbour, called by controller
    def add_connection(self, target_node):
        self.connections.append(target_node)
        self.make_subscriptions()

    #Publish service with room_id on oneself and subscribe to room on previous Node and oneself  
    def propagate_request(self, service, request_id, room_id, parent_id=None):
        if parent_id == None:
            parent_room_topic = None
        else:
            parent_room_topic = "{}/{}/{}".format(parent_id, service, room_id)
            self.client.subscribe(parent_room_topic, qos=2)
        self.publish(
            "{}/{}".format(self.client_id, service),
            "{},{}".format(request_id, room_id) 
            )
        self_room_topic = "{}/{}/{}".format(self.client_id, service, room_id)
        self.client.subscribe(self_room_topic, qos=2)
        self.active_rooms[self_room_topic] = parent_room_topic
        return self_room_topic

    #Decide to process service or not
    def handle_item(self, service, request_id, room_topic):
        if self.services[service] >= Catalogue.services[service]["asking_price"]: #Checking against asking price
            self.process_service(service=service, request_id=request_id, room_topic=room_topic)
    
    #Calculates processing time and "processes" service in its own thread
    def process_service(self, service, request_id, room_topic):
        self.request_monitor.start_processing(request_id=int(request_id), node_id=self.client_id)
        bid = self.services[service]
        std_processing_duration = Catalogue.services[service]["std_process_t"]
        process_duration = std_processing_duration*(1+ProcessingConfig.processing_constant*(50-bid)/50)
        t_service_process = Timer(interval=process_duration, function=self.complete_processing, kwargs={"request_id":int(request_id), "room_topic":room_topic})
        t_service_process.start()
        self.active_processes[room_topic] = {"t_process": t_service_process, "request_id": int(request_id)}

    #Function in timer thread has been executed and processing is completed
    def complete_processing(self, request_id, room_topic):
        self.active_processes.pop(room_topic)
        self.client.publish(room_topic, "end")
        self.request_monitor.complete_processing(request_id=request_id, node_id=self.client_id)

    #Cancel timer thread for process and notify request monitor
    def abort_processing(self, t_process, request_id):
        t_process.cancel()
        self.request_monitor.abort_processing(request_id=request_id, node_id=self.client_id)

    def increment_room_pointer(self):
        self.room_pointer += 1
        if self.room_pointer == len(self.rooms):
            self.room_pointer = 0

    #QoS level 2 publish method
    def publish(self, topic, payload):
        self.client.publish(topic, payload, qos=2)

    def __repr__(self) -> str:
        return self.client_id
