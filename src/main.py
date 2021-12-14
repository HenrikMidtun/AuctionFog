from os import name
from time import sleep
from mqtt_clients.AuctionNode import AuctionNode
from mqtt_clients.ChoiceNode import ChoiceNode
from mqtt_clients.Client import Client
from NodeController import NodeController
from RequestMonitor import RequestMonitor
from FileWriter import RunWriter
from Grapher import BarGrapher
from NetworkController import NetworkController


"""
    Creates a network with randomized bids and set structure
    Does a run in batches, because there is a max limit to how many Nodes that can run simultaneously (somewhere between 180 and 420 nodes)
    Writes the results to separate files for each type
"""
def run_net2(factory: NetworkController, request_monitor: RequestMonitor, filename, structure={0: [1,2],1: [3,4],2: [5,6]} , n_type="all", strength=50):
    writer = RunWriter(request_monitor=request_monitor)
    writer.set_headers(filename=filename)

    
    """
        Create Nodes of all types and make connections according to structure
    """
    requests = {"auction": [], "choice": [], "battistoni": []}
    origin_nodes = {"auction":[], "choice":[], "battistoni":[]}
    for k in range(15): #Batch size, number of networks of each type run simultaneously 
        for type, node_obj in network_controller.create_network(structure=structure, n_type=n_type, strength=strength).items():
            origin_nodes[type].append(node_obj)

    """
        Make Requests to origin Nodes and update all Node bids in batches.
    """
    client = Client(request_monitor=request_monitor)
    for i in range(10): #Amount of RUNs
        for type, o_nodes in origin_nodes.items():
            for node in o_nodes:
                req_id = client.make_request(origin_node_id=node.client_id, service="A")
                requests[type].append(req_id)

        sleep(6) #Allow Nodes to finish up processes
        network_controller.updateNetworkServices(strength=strength) #Update bids (and services) of Nodes

    """
        Write requests to file
    """
    for n_type, req_ids in requests.items():
        print(n_type)
        for req in req_ids:
            print("writing for request", req)
            writer.write_request_results(filename=filename, request_id=req, n_type=n_type)
        
"""
Creates the first test network, a 7 node binary tree with predetermined bids
"""
def create_plot_net1(factory:NetworkController, request_monitor:RequestMonitor):
    writer = RunWriter(request_monitor=request_monitor)

    origin_nodes = factory.create_net1()
    filenames = ["auction", "choice", "battistoni"]
    name_index = 0
    for node in origin_nodes:

        client = Client(origin_node_id=node.client_id, request_monitor=request_monitor)

        req_ids = []
        for i in range(10):
            req_id = client.make_request(service="A")
            req_ids.append(req_id)

        sleep(7)

        writer.set_active_filename(filename=filenames[name_index])

        for req in req_ids:
            writer.write_request_results(request_id=req)

        
        bar_grapher.create_bar_graph(filenames[name_index], filenames[name_index])
        name_index += 1
        sleep(3)

net1 = {
        0: [1,2],
        1: [3,4],
        2: [5,6]
    }
net2 = {
        0: [1,2,3,4,5,6,7,8,9],
        1: [11,12],
        2: [13,14]
    }
net3 = {
        0: [1,2],
        1: [3,4],
        2: [5,6],
        3: [7,8],
        4: [9,10],
        7: [11,12],
        11: [13,14]
    }

request_monitor = RequestMonitor()
node_controller = NodeController(request_monitor=request_monitor)
network_controller = NetworkController(node_controller)
bar_grapher = BarGrapher()

filename = "test"#"Net2Runs500Meanbid50"
subtitle = "Network 2, 500 runs, mean bid = 50"
run_net2(network_controller,request_monitor, structure=net2, n_type="auction", filename=filename)
bar_grapher.graph_completion_time(filename, filename, subtitle=subtitle)
bar_grapher.graph_processing_time(filename, filename, subtitle=subtitle)