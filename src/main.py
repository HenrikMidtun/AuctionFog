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
    Creating Nodes one by one with set capabilities
"""

request_monitor = RequestMonitor()
node_controller = NodeController(request_monitor=request_monitor)
network_controller = NetworkController(node_controller)

"""
    Creates a network with randomized bids and set structure
    Creates plots for these runs
"""
def create_plot_net2(factory: NetworkController, request_monitor: RequestMonitor, n_type="all"):
    filenames = ["randombids_auction", "randombids_choice", "randombids_battistoni"]
    writer = RunWriter(request_monitor=request_monitor)
    for f_name in filenames:
        writer.set_headers(filename=f_name)

    requests = {"auction": [], "choice": [], "battistoni": []}
    
    """
        Create Nodes of all types and make connections according to structure
    """
    structure = {
                0: [1,2],
                1: [3,4],
                2: [5,6]
            }
    origin_nodes = {"auction":[], "choice":[], "battistoni":[]}
    for k in range(5): #Batch size, number of networks of each type run simultaneously 
        for type, node_obj in network_controller.create_network(structure=structure, n_type=n_type).items():
            origin_nodes[type].append(node_obj)

    """
        Make Requests and update Node bids in batches.
    """
    client = Client(request_monitor=request_monitor)
    for i in range(5): #Amount of RUNs
        for type, o_nodes in origin_nodes.items():
            for node in o_nodes:
                req_id = client.make_request(origin_node_id=node.client_id, service="A")
                requests[type].append(req_id)

        sleep(6) #Allow Nodes to finish up processes
        network_controller.updateNetworkServices() #Update bids (and services) of Nodes

    """
        Write requests to file
    """
    for req_type, req_ids in requests.items():
        for req in req_ids:
            print("writing for request", req)
            writer.write_request_results(filename="randombids_{}".format(req_type), request_id=req)

    bar_grapher = BarGrapher()
    for f_name in filenames:
        bar_grapher.create_bar_graph(f_name, f_name)
        


"""
Creates the first test network, a 7 node binary tree with predetermined bids
"""
def create_plot_net1(factory:NetworkController, request_monitor:RequestMonitor):
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

        writer = RunWriter(request_monitor=request_monitor)
        writer.set_active_filename(filename=filenames[name_index])

        for req in req_ids:
            writer.write_request_results(request_id=req)

        bar_grapher = BarGrapher()
        bar_grapher.create_bar_graph(filenames[name_index], filenames[name_index])
        name_index += 1
        sleep(3)


create_plot_net2(network_controller,request_monitor, n_type="battistoni")