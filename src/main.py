from time import sleep
from mqtt_clients.AuctionNode import AuctionNode
from mqtt_clients.ChoiceNode import ChoiceNode
from mqtt_clients.Client import Client
from NodeController import NodeController
from RequestMonitor import RequestMonitor
from FileWriter import RunWriter
from Grapher import BarGrapher
from FogFactory import FogFactory

"""
    Creating Nodes one by one with set capabilities
"""

request_monitor = RequestMonitor()
controller = NodeController(request_monitor=request_monitor)
factory = FogFactory(controller)
origin_nodes = factory.create_random_net1()

filenames = ["r_auction", "r_choice", "r_battistoni"]
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


