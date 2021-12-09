from mqtt_clients.AuctionNode import AuctionNode
from mqtt_clients.ChoiceNode import ChoiceNode
from mqtt_clients.BattistoniNode import BattistoniNode

import random
from RequestMonitor import RequestMonitor

class NodeController:

    def __init__(self, request_monitor: RequestMonitor):
        self.index = 0
        self.nodes = []
        self.request_monitor = request_monitor

    """
        Creates N amount of Nodes that have a certain probability to contain a service.
        The given strength sets a baseline and any bid the Node produces is in a +-20% range from the strength given.
        The randomness is good to produce unique cases that involves many Nodes

        Creates an equal amount of auction, random choice, and Battistoni Nodes !Not implemented!
    """
    def createNodes(self, amount_nodes, service_probabilities: dict, strength=80):
        new_nodes = []
        for i in range(amount_nodes):
            node_services = {}
            for k,v in service_probabilities.items():
                decider = random.random()*100
                if decider < v:
                    node_services[k] = min(int(random.randrange(80,121,1)/100*strength),100) #Setting the bidding price
            n = AuctionNode(client_id="Node_{}".format(self.index), request_monitor=self.request_monitor, services=node_services)
            self.index+=1
            new_nodes.append(n)
        
        self.nodes = self.nodes+new_nodes
        return new_nodes

    """
        This creates a single Node with no random attributes.
        This is useful for small case examples to test certain cases.
    """
    def createAuctionNode(self, services_bids: dict):
        new_node = AuctionNode(client_id="Node_{}".format(self.index), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        self.nodes.append(new_node)
        return new_node

    def createChoiceNode(self, services_bids: dict):
        new_node = ChoiceNode(client_id="Node_{}".format(self.index), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        self.nodes.append(new_node)
        return new_node
    
    def createBattistoniNode(self, services_bids: dict):
        new_node = BattistoniNode(client_id="Node_{}".format(self.index), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        self.nodes.append(new_node)
        return new_node

    #Connects Nodes to each other, default is one-directional relationship
    def connectNodes(self, connecting_node, target_node, bidirectional=False):
        valid_nodes=True
        if connecting_node not in self.nodes:
            print("{} does not exist!".format(connecting_node))
            valid_nodes=False
        if target_node not in self.nodes:
            print("{} does not exist!".format(target_node))
            valid_nodes=False
        if not valid_nodes:
            return
        
        connecting_node.add_connection(target_node.client_id)