import csv
from RequestMonitor import RequestMonitor

class RunWriter:

    def __init__(self, request_monitor:RequestMonitor):
        self.folder_location = "/home/house/AuctionFog/output/runs"
        self.request_monitor = request_monitor
        self.header = ['n_type', 'request_id', 'completion_time', 'total_processing_time']

    #Set new active filename and write header
    def set_headers(self, filename):
        with open("{}/{}.csv".format(self.folder_location, filename), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

    #Writes the results of a request as a line in the given csv file.
    def write_request_results(self, filename, request_id, n_type):
        completion_time = self.request_monitor.get_completion_time(request_id=request_id)
        total_processing_time = self.request_monitor.get_total_processing_time(request_id=request_id)
        with open("{}/{}.csv".format(self.folder_location, filename), 'a') as f:
            writer = csv.writer(f)
            writer.writerow([n_type, request_id, completion_time, total_processing_time])

"""
Creates a file for each run.
Each request has its own line that includes the completion time, and total processing time.
Each file includes multiple requests
Each line includes the network type that the request was sent to.
"""