import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5
from mqtt_clients.Node import Node

# The callback for when the client receives a CONNACK response from the server.

class Client:

    def __init__(self, origin_node: Node):
        """
            Application
        """
        self.origin_node = origin_node
        self.request_topic = "{}/request".format(self.origin_node)
        """
            Paho MQTT Client
        """
        self.client = mqtt.Client(client_id="Client", protocol=MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        #subscribe to response topic for origin node
        pass
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def make_request(self, service):
        self.client.publish(self.request_topic, service)

