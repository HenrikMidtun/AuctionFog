from typing import no_type_check
from RequestMonitor import RequestMonitor
from NodeController import NodeController

class NetworkController:

    def __init__(self, controller: NodeController):
        self.controller = controller
        self.networks = []


#[{0: {'auction': Node_0}, 1: {'auction': Node_1}, 2: {'auction': Node_2}, 3: {'auction': Node_3}, 4: {'auction': Node_4}, 5: {'auction': Node_5}}, {0: {'auction': Node_6}, 1: {'auction': Node_7}, 2: {'auction': Node_8}, 3: {'auction': Node_9}, 4: {'auction': Node_10}, 5: {'auction': Node_11}}, {0: {'auction': Node_12}, 1: {'auction': Node_13}, 2: {'auction': Node_14}, 3: {'auction': Node_15}, 4: {'auction': Node_16}, 5: {'auction': Node_17}}, {0: {'auction': Node_18}, 1: {'auction': Node_19}, 2: {'auction': Node_20}, 3: {'auction': Node_21}, 4: {'auction': Node_22}, 5: {'auction': Node_23}}, {0: {'auction': Node_24}, 1: {'auction': Node_25}, 2: {'auction': Node_26}, 3: {'auction': Node_27}, 4: {'auction': Node_28}, 5: {'auction': Node_29}}]
    def updateNetworkServices(self, service_probabilities={"A":100}, strength=50):
        for fog in self.networks:
            for index, nodes in fog.items():
                nodes_to_update = []
                for node in nodes.values():
                    nodes_to_update.append(node)
                self.controller.updateNodeServices(nodes_to_update, service_probabilities=service_probabilities, strength=strength)

    """
    Creates three directed graphs of Nodes, one graph for each type
        Input -> Dict, Services, Strength
            {
                0: [1,2,3],
                2: [4,5]
            }
                 0
               / | \
              1  2  3
                / \
               4   5
        Output -> Three Origin Nodes

        *Intended origin Node is always given as 0 in the structure
    """
    def create_network(self, structure: dict, n_type="all", services={"A":100}, strength=50):
        created_nodes = {}
        origin_nodes = {}
        for k,v in structure.items():
            if k not in created_nodes.keys():
                created_nodes[k] = self.controller.createNodes(service_probabilities=services, strength=strength, n_type=n_type)
            for node in v:
                if node not in created_nodes.keys():
                    created_nodes[node] = self.controller.createNodes(service_probabilities=services, strength=strength, n_type=n_type)
                    for type, node_obj in created_nodes[node].items():
                        self.controller.connectNodes(node_obj, created_nodes[k][type])
        origin_nodes = created_nodes[0] #Assuming that intended origin Node is always given as 0 in the structure
        self.networks.append(created_nodes)
        return origin_nodes

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
        nodes = self.controller.createNodes(amount_nodes=7, service_probabilities={"A":80}, strength=50)
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