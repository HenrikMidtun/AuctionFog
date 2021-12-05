from time import sleep
from mqtt_clients.Node import Node
from mqtt_clients.Client import Client
from NodeController import NodeController
from RequestMonitor import RequestMonitor
from FileWriter import RunWriter
"""
amount_nodes = 3
service_probabilities = {"A": 100, "B":40, "C":50}
controller = NodeController()

new_nodes = controller.createNodes(amount_nodes=amount_nodes, service_probabilities=service_probabilities)
print(controller.nodes)
controller.connectNodes(controller.nodes[0],controller.nodes[1]) #Node_0 subscribes to Node_1's auctions
controller.connectNodes(controller.nodes[2],controller.nodes[0])

client = Client(origin_node=controller.nodes[1]) #Node_1 is the origin Node
client.make_request(service="A")
"""
"""

req_id = request_monitor.get_request_id()
print("request id", req_id)

request_monitor.start_request(req_id)
sleep(1)
request_monitor.start_processing(req_id,"Node_0")
sleep(2)
request_monitor.complete_processing(req_id,"Node_0")
print(request_monitor.get_processing_time(req_id))
print(request_monitor.get_completion_time(req_id))
"""
request_monitor = RequestMonitor()
controller = NodeController(request_monitor=request_monitor)

n0 = controller.createNode(services_bids={"A": 40})
n1 = controller.createNode(services_bids={"A": 100})
n2 = controller.createNode(services_bids={"A": 100})

controller.connectNodes(n1,n0)
controller.connectNodes(n2,n0)

client = Client(origin_node=n0, request_monitor=request_monitor)
req_id = client.make_request(service="A")

sleep(5)
"""
com_time = request_monitor.get_completion_time(req_id)
proc_time = request_monitor.get_total_processing_time(req_id)

print("total time before request served", com_time)
print("total processing time", proc_time)
nodes_req1 = request_monitor.get_processing_times(req_id)
print(nodes_req1)
"""

writer = RunWriter(request_monitor=request_monitor)

writer.set_active_filename(filename="test")
writer.write_request_results(request_id=req_id)



