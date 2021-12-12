from platform import node
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5
from threading import Timer
from Configuration import Catalogue, ProcessingConfig
from RequestMonitor import RequestMonitor
import random

# The callback for when the client receives a CONNACK response from the server.

class ChoiceNode:
    def __init__(self, client_id, request_monitor: RequestMonitor, services:dict={"A": 100}):
        """
            Application
        """
        self.client_id = str(client_id)
        self.request_monitor = request_monitor
        self.services = services
        self.connections = [] #List of Node ids that should be subscribed to, i.e., Node_1
        self.neighbours = []
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
        #print("{}: {} {}".format(self.client_id, msg.topic, str(msg.payload)))

        #Incomming request from Client
        if msg.topic == "{}/request".format(self.client_id):
            [request_id, requested_service] = msg.payload.decode("utf-8").split(",") #Convert from bytes to string
            self.handle_item(service=requested_service, request_id=request_id)

        if msg.topic == "{}/connect".format(self.client_id):
            neighbour_id = msg.payload.decode("utf-8") #Convert from bytes to string
            self.add_neighbour(neighbour_id=neighbour_id)

    """
        Node Methods
    """
    def make_subscriptions(self):
        self.client.subscribe("{}/#".format(self.client_id), qos=2)

    #Connect to a node as a neighbour, called by controller
    def add_connection(self, target_node):
        self.publish("{}/connect".format(target_node), self.client_id)

    #Decide to process service or propagate item 
    def handle_item(self, service, request_id):
        if service in self.services:
            if self.services[service] < Catalogue.services[service]["asking_price"] and len(self.neighbours) != 0: #Checking against asking price
                self.propagate_request(service=service, request_id=request_id)
            else:
                self.process_service(service=service, request_id=request_id)
        else:
            self.propagate_request(service, request_id=request_id)
    
    #Calculates processing time and "processes" service in its own thread
    def process_service(self, service, request_id):
        self.request_monitor.start_processing(request_id=int(request_id), node_id=self.client_id)
        bid = self.services[service]
        std_processing_duration = Catalogue.services[service]["std_process_t"]
        process_duration = std_processing_duration*(1+ProcessingConfig.processing_constant*(50-bid)/50)
        t_service_process = Timer(interval=process_duration, function=self.request_monitor.complete_processing, kwargs={"request_id":int(request_id), "node_id":self.client_id})
        t_service_process.setDaemon(True)
        t_service_process.start()

    #Publishes request to a random neighbour
    def propagate_request(self, service, request_id):
        neighbour = self.choose_neighbour()
        self.publish(
            "{}/request".format(neighbour), 
            "{},{}".format(request_id, service)
            )
        print("{}: Propagating request {} of service {} to {}.".format(self.client_id, request_id, service, neighbour))

    #Randomly selects a neighbour and returns neighbour id
    def choose_neighbour(self):
        neighbour = self.neighbours[random.randint(0, len(self.neighbours)-1)]
        return neighbour

    def add_neighbour(self, neighbour_id: str):
        if neighbour_id not in self.neighbours:
            self.neighbours.append(neighbour_id)
            #print("{}: Included {} as a neighbour.".format(self.client_id, neighbour_id))
        else:
            #print("{}: Already have {} as a neighbour.".format(self.client_id, neighbour_id))
            pass
        
    #QoS level 2 publish method
    def publish(self, topic, payload):
        self.client.publish(topic, payload, qos=2)

    def update_services(self, new_services):
        print("{}: Services updated to {}.".format(self.client_id, new_services))
        self.services = new_services

    def __repr__(self) -> str:
        return self.client_id
