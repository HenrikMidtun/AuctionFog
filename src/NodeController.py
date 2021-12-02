from mqtt_clients.Node import Node
import random

class NodeController:

    def __init__(self):
        self.index = 0
        self.nodes = []
        
    def createNodes(self, amount_nodes, service_probabilities: dict):
        new_nodes = []
        for i in range(amount_nodes):
            node_services = {}
            for k,v in service_probabilities.items():
                decider = random.random()*100
                if decider < v:
                    node_services[k] = 0
            n = Node(client_id="Node_{}".format(self.index), services=node_services)
            self.index+=1
            new_nodes.append(n)
        
        self.nodes = self.nodes+new_nodes    
        return new_nodes

    def connectNodes(self, subscribing_node: Node, target_node: Node, bidirectional=False):
        valid_nodes=True
        if subscribing_node not in self.nodes:
            print("{} does not exist!".format(subscribing_node))
            valid_nodes=False
        if target_node not in self.nodes:
            print("{} does not exist!".format(target_node))
            valid_nodes=False
        if not valid_nodes:
            return
        
        subscribing_node.add_connection(target_node.client_id)