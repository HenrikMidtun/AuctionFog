from typing import no_type_check
from RequestMonitor import RequestMonitor
from NodeController import NodeController

class NetworkController:

    def __init__(self, controller: NodeController):
        self.controller = controller
        self.networks = []

    """
    Update bids on services for all Nodes.
    The differently typed Nodes that represent the same network will have the same updated bids
    """
    def updateNetworkServices(self, service_probabilities={"A":100}):
        for fog in self.networks:
            for index, nodes in fog.items():
                nodes_to_update = []
                for node in nodes.values():
                    nodes_to_update.append(node)
                self.controller.updateNodeServices(nodes_to_update, service_probabilities=service_probabilities)

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
    def create_network(self, structure: dict, n_type="all", services={"A":100}):
        created_nodes = {}
        origin_nodes = {}
        for k,v in structure.items():
            if k not in created_nodes.keys():
                created_nodes[k] = self.controller.createNodes(service_probabilities=services, n_type=n_type)
            for node in v:
                if node not in created_nodes.keys():
                    created_nodes[node] = self.controller.createNodes(service_probabilities=services, n_type=n_type)
                    for type, node_obj in created_nodes[node].items():
                        self.controller.connectNodes(node_obj, created_nodes[k][type])
        origin_nodes = created_nodes[0] #Assuming that intended origin Node is always given as 0 in the structure
        self.networks.append(created_nodes)
        return origin_nodes
