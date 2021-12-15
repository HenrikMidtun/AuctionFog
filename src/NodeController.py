from mqtt_clients.AuctionNode import AuctionNode
from mqtt_clients.ChoiceNode import ChoiceNode
from mqtt_clients.BattistoniNode import BattistoniNode

import random
from RequestMonitor import RequestMonitor

class NodeController:

    def __init__(self, request_monitor: RequestMonitor):
        self.index = 0
        #self.nodes = []
        self.request_monitor = request_monitor
        self.node_classes = {"auction": AuctionNode, "choice": ChoiceNode, "battistoni": BattistoniNode}
        random.seed(0)

    """
        Creates 3 Nodes that have a certain probability to contain a service.
        The given strength sets a baseline and any bid the Node produces is in a +-50% range from the strength given.
        The randomness is good to produce unique cases that involves many Nodes

        Creates auction, random choice, and Battistoni Nodes with equal bids.
    """
    def createNodes(self, service_probabilities: dict, strength=50, n_type="all"):
        print(n_type)
        if n_type not in ["all","auction", "choice", "battistoni"]:
            print("{} is not a valid type ['all', 'auction', 'choice', 'battistoni'".format(n_type))
            return 
        nodes = {}
        services = self.getRandomBids(service_probabilities=service_probabilities, strength=strength)
        if n_type == "all":
            auction_node = AuctionNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services)
            nodes["auction"] = auction_node
            choice_node = ChoiceNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services)
            nodes["choice"] = choice_node
            battistoni_node = BattistoniNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services)
            nodes["battistoni"] = battistoni_node
        else:
            node = self.node_classes[n_type](client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services)
            nodes[n_type] = node
        return nodes

    """
        This creates a single Node with no random attributes.
        This is useful for small case examples to test certain cases.
    """
    def createAuctionNode(self, services_bids: dict):
        new_node = AuctionNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        return new_node

    def createChoiceNode(self, services_bids: dict):
        new_node = ChoiceNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        return new_node
    
    def createBattistoniNode(self, services_bids: dict):
        new_node = BattistoniNode(client_id="Node_{}".format(self.getIndex()), request_monitor=self.request_monitor, services=services_bids)
        self.index+=1
        return new_node

    #Connects Nodes to each other, default is one-directional relationship
    def connectNodes(self, connecting_node, target_node, bidirectional=False):
        connecting_node.add_connection(target_node.client_id)

    """
        Generates random bids for the given service probabilities and strength
    """
    def getRandomBids(self, service_probabilities: dict, strength=50):
        node_servicebids = {}
        for k,v in service_probabilities.items():
            decider = random.random()*100
            if decider < v:
                node_servicebids[k] = min(int(random.randrange(100-50,100+51,1)/100*strength),100) #Setting the bidding price, may switch to std distribution
        return node_servicebids
    
    """
        Picks a random *rounded* integer from a normal distribution centered around the given strength.
        The random integer returned is within [0,100] because it represents a bid
        Note, 68% of values fall within 1 standard deviation, 95% within 2 standard deviations, 99.9% within 3 standard deviations

    """
    def getNormalisedRandomBids(self, service_probabilities: dict, strength=50, std_dev=15):
        mean = strength
        node_servicebids = {}
        for k,v in service_probabilities.items():
            decider = random.random()*100
            if decider < v:
                while True:
                    x = round(random.normalvariate(mean, std_dev))
                    if x >= 0 and x <= 100:
                        node_servicebids[k] = x
                        break
        return node_servicebids

    def updateNodeServices(self, node_objs, service_probabilities: dict, strength=50, std_dev=15):
        node_servicebids = self.getNormalisedRandomBids(service_probabilities=service_probabilities, strength=strength, std_dev=std_dev)
        for node in node_objs:
            node.update_services(node_servicebids)

    def getIndex(self):
        index = self.index
        self.index += 1
        return index