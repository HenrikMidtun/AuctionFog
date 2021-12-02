from time import sleep
from mqtt_clients.Node import Node
from NodeController import NodeController

amount_nodes = 2
service_probabilities = {"A": 70, "B":40, "C":50}
controller = NodeController()
new_nodes = controller.createNodes(amount_nodes=amount_nodes, service_probabilities=service_probabilities)
print(controller.nodes)
controller.connectNodes(controller.nodes[0],controller.nodes[1])
controller.nodes[1].publish("Node_1/test", "hello")

sleep(5)