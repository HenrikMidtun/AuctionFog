from os import name
from time import sleep
from mqtt_clients.AuctionNode import AuctionNode
from mqtt_clients.ChoiceNode import ChoiceNode
from mqtt_clients.Client import Client
from NodeController import NodeController
from RequestMonitor import RequestMonitor
from FileWriter import SessionWriter, AnalyticsWriter
from Grapher import BarGrapher
from NetworkController import NetworkController


"""
    Creates a network with randomized bids and set structure
    Does a run in batches, because there is a max limit to how many Nodes that can run simultaneously (somewhere between 180 and 420 nodes)
    Writes the results to separate files for each type
"""
def run_sim(network_controller: NetworkController, request_monitor: RequestMonitor, filename, structure={0: [1,2],1: [3,4],2: [5,6]} , n_type="all"):
    """
        Create Nodes of all types and make connections according to structure
    """
    requests = {"auction": [], "choice": [], "battistoni": []}
    origin_nodes = {"auction":[], "choice":[], "battistoni":[]}
    for k in range(5): #Batch size, number of networks of each type run simultaneously 
        for type, node_obj in network_controller.create_network(structure=structure, n_type=n_type).items():
            origin_nodes[type].append(node_obj)

    """
        Make Requests to origin Nodes and update all Node bids in batches.
    """
    client = Client(request_monitor=request_monitor)
    for i in range(3): #Amount of batched iterations
        for type, o_nodes in origin_nodes.items():
            for node in o_nodes:
                req_id = client.make_request(origin_node_id=node.client_id, service="A")
                requests[type].append(req_id)

        sleep(6) #Allow Nodes to finish up processes
        network_controller.updateNetworkServices(service_probabilities={"A":100}) #Update bids (and services) of Nodes

    """
        Write requests to file
    """
    sleep(10)
    writer = SessionWriter(request_monitor=request_monitor)
    writer.set_headers(filename=filename)

    for n_type, req_ids in requests.items():
        print(n_type)
        for req in req_ids:
            print("writing for request", req)
            writer.write_request_results(filename=filename, request_id=req, n_type=n_type)
        

net1 = {
        0: [1,2],
        1: [3,4],
        2: [5,6],
        3: [7,8],
        4: [9,10],
        5: [11,12],
        6: [13,14]
    }

net2 = {
        0: [1,2],
        1: [3],
        2: [4],
        3: [5],
        4: [6],
        5: [7,8],
        6: [9,10],
        7: [11],
        8: [12],
        9: [13],
        10: [14]
    }
net3 = {
        0: [1,2,3,4],
        1: [5,6,7],
        2: [8,9],
        3: [10,11],
        4: [12,13,14]
    }

request_monitor = RequestMonitor()
node_controller = NodeController(request_monitor=request_monitor)
network_controller = NetworkController(node_controller)
filename = "default"
run_sim(network_controller,request_monitor, structure=net1, n_type="all", filename=filename)

#bar_grapher = BarGrapher()
#subtitle = "Network 1, 500 runs, Mean Bid=50, SD=20, Asking Price=50, k=0.5"
#bar_grapher.graph_completion_time(filename, filename, subtitle=subtitle)
#bar_grapher.graph_processing_time(filename, filename, subtitle=subtitle)

#session_sources = []
#subtitle = ""
#bar_grapher.graph_comparison_compl_t(session_sources=session_sources, graph_filename="net", label="", groups=[], subtitle=subtitle)
#bar_grapher.graph_comparison_proc_t(session_sources=session_sources, graph_filename="net", label="", groups=[], subtitle=subtitle)

#filewriter = AnalyticsWriter()
#variable = "topology"
#sessions = {"Net1":"topology/Net1Runs500Meanbid50SD20","Net2":"topology/Net2Runs500Meanbid50SD20","Net3":"topology/Net3Runs500Meanbid50SD20"}
#filewriter.write_analytics_file("topology", sessions, variable)
