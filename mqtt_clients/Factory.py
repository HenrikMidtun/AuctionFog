from mqtt_clients.Node import Node
import random

class Factory:

    def __init__(self, amount_nodes, service_probabilities: dict):
        
        for i in range(amount_nodes):
            node_services = {}
            for k,v in service_probabilities.items():
                decider = random.random()*100
                if decider < v:
                    node_services[k] = 0
            n = Node(client_id="Node_{}".format(i), services=node_services)

