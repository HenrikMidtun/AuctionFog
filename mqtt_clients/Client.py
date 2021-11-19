import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv5

# The callback for when the client receives a CONNACK response from the server.

class Client:

    def __init__(self):
        self.client = mqtt.Client(client_id="Client", protocol=MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Connected with result code "+str(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("response/#")
        client.publish("request/serviceA", "hello world!")
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
    

my_node = Client()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.