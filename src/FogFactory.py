from RequestMonitor import RequestMonitor
from NodeController import NodeController

class FogFactory:

    def __init__(self, controller: NodeController):
        self.controller = controller
    
    #A binomial tree that contains 7 Nodes and is 3 levels deep
    #Returns origin Node for [Auction, Choice, Battistoni]
    def create_net1(self):
        n0 = self.controller.createAuctionNode(services_bids={"A": 30})
        n1 = self.controller.createAuctionNode(services_bids={"A": 25})
        n2 = self.controller.createAuctionNode(services_bids={"A": 30})
        n3 = self.controller.createAuctionNode(services_bids={"A": 60})
        n4 = self.controller.createAuctionNode(services_bids={"A": 55})
        n5 = self.controller.createAuctionNode(services_bids={"A": 40})
        n6 = self.controller.createAuctionNode(services_bids={"A": 80})
        self.controller.connectNodes(n1,n0)
        self.controller.connectNodes(n2,n0)
        self.controller.connectNodes(n3,n1)
        self.controller.connectNodes(n4,n1)
        self.controller.connectNodes(n5,n2)
        self.controller.connectNodes(n6,n2)
        auction_node = n0
        n0 = self.controller.createChoiceNode(services_bids={"A": 30})
        n1 = self.controller.createChoiceNode(services_bids={"A": 25})
        n2 = self.controller.createChoiceNode(services_bids={"A": 30})
        n3 = self.controller.createChoiceNode(services_bids={"A": 60})
        n4 = self.controller.createChoiceNode(services_bids={"A": 55})
        n5 = self.controller.createChoiceNode(services_bids={"A": 40})
        n6 = self.controller.createChoiceNode(services_bids={"A": 80})
        self.controller.connectNodes(n1,n0)
        self.controller.connectNodes(n2,n0)
        self.controller.connectNodes(n3,n1)
        self.controller.connectNodes(n4,n1)
        self.controller.connectNodes(n5,n2)
        self.controller.connectNodes(n6,n2)
        choice_node = n0
        #Battistoni
        n0 = self.controller.createBattistoniNode(services_bids={"A": 30})
        n1 = self.controller.createBattistoniNode(services_bids={"A": 25})
        n2 = self.controller.createBattistoniNode(services_bids={"A": 30})
        n3 = self.controller.createBattistoniNode(services_bids={"A": 60})
        n4 = self.controller.createBattistoniNode(services_bids={"A": 55})
        n5 = self.controller.createBattistoniNode(services_bids={"A": 40})
        n6 = self.controller.createBattistoniNode(services_bids={"A": 80})
        self.controller.connectNodes(n1,n0)
        self.controller.connectNodes(n2,n0)
        self.controller.connectNodes(n3,n1)
        self.controller.connectNodes(n4,n1)
        self.controller.connectNodes(n5,n2)
        self.controller.connectNodes(n6,n2)
        battistoni_node = n0
        return [auction_node, choice_node, battistoni_node]

    #A Random binomial tree, 7 Nodes, 3 levels deep, random bids
    def create_random_net1(self):
        nodes = self.controller.createNodes(amount_nodes=7, service_probabilities={"A":100}, strength=40)
        auction_nodes = nodes["auction_nodes"]
        choice_nodes = nodes["choice_nodes"]
        battistoni_nodes = nodes["battistoni_nodes"]
        for i in range(3):
            if i == 0:
                n = auction_nodes
            elif i == 1:
                n = choice_nodes
            elif i == 2:
                n = battistoni_nodes
            self.controller.connectNodes(n[2],n[0])
            self.controller.connectNodes(n[3],n[1])
            self.controller.connectNodes(n[4],n[1])
            self.controller.connectNodes(n[5],n[2])
            self.controller.connectNodes(n[6],n[2])
        return [auction_nodes[0], choice_nodes[0], battistoni_nodes[0]]