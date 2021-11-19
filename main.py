from time import sleep
from mqtt_clients.Factory import Factory

amount_nodes = 5
service_probabilities = {"A": 70, "B":40, "C":50}
my_factory = Factory(amount_nodes=amount_nodes, service_probabilities=service_probabilities)

sleep(5)