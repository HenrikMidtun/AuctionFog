from time import sleep
from mqtt_clients.Node import Node
from mqtt_clients.Client import Client
from NodeController import NodeController

"""
amount_nodes = 3
service_probabilities = {"A": 100, "B":40, "C":50}
controller = NodeController()

new_nodes = controller.createNodes(amount_nodes=amount_nodes, service_probabilities=service_probabilities)
print(controller.nodes)
controller.connectNodes(controller.nodes[0],controller.nodes[1]) #Node_0 subscribes to Node_1's auctions
controller.connectNodes(controller.nodes[2],controller.nodes[0])

client = Client(origin_node=controller.nodes[1]) #Node_1 is the origin Node
client.make_request(service="A")
"""

controller = NodeController()

n0 = controller.createNode(services_bids={"A": 40})
n1 = controller.createNode(services_bids={"A": 100})
n2 = controller.createNode(services_bids={"A": 100})

controller.connectNodes(n1,n0)
controller.connectNodes(n2,n1)

client = Client(origin_node=n0)
client.make_request(service="A")

sleep(10)