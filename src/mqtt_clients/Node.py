import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5

# The callback for when the client receives a CONNACK response from the server.

class Node:
    def __init__(self, client_id, services={"A": 0, "B": 0}):
        """
            Application
        """
        self.client_id = str(client_id)
        self.services = services
        self.connections = [] #List of Node ids that should be subscribed to, i.e., Node_1
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
        self.make_subscriptions(client)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("{}: {} {}".format(self.client_id, msg.topic, str(msg.payload)))

    def make_subscriptions(self, client):
        client.subscribe("{}/#".format(self.client_id))

        for node in self.connections:
            client.subscribe("{}/#".format(node)) #Subscribe to neighbour Node
    
    def add_connection(self, node_id: str):
        if node_id not in self.connections:
            self.connections.append(node_id)
            self.client.subscribe("{}/#".format(node_id)) #Subscribe to neighbour Node
        else:
            print("{}: Already Connected to {}.".format(self.client_id, node_id))

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        
    def __repr__(self) -> str:
        return self.client_id

if __name__ == "__main__":
    no = Node(client_id=Node)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.