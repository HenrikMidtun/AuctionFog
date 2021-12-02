from time import sleep
from mqtt_clients.Node import Node
from mqtt_clients.Client import Client
from NodeController import NodeController

amount_nodes = 2
service_probabilities = {"A": 100, "B":40, "C":50}
controller = NodeController()

new_nodes = controller.createNodes(amount_nodes=amount_nodes, service_probabilities=service_probabilities)
print(controller.nodes)
controller.connectNodes(controller.nodes[0],controller.nodes[1]) #Node_0 subscribes to Node_1's auctions
#controller.nodes[1].publish("Node_1/auction/room_3", "hello")

client = Client(origin_node=controller.nodes[1]) #Node_1 is the origin Node
client.make_request(service="A")

sleep(1)

print(controller.nodes[0].active_auctions_bidding)


sleep(5)