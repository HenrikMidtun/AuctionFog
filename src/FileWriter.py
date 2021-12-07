import csv
from RequestMonitor import RequestMonitor

class RunWriter:

    def __init__(self, request_monitor:RequestMonitor):
        self.folder_location = "/home/house/AuctionFog/output/runs"
        self.active_filename = None
        self.request_monitor = request_monitor
        self.header = ['request_id', 'completion_time', 'total_processing_time']

    #Set new active filename and write header
    def set_active_filename(self, filename):
        self.active_filename = filename
        with open("{}/{}.csv".format(self.folder_location, filename), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

    #Writes the results of a request as a line in the active csv file.
    def write_request_results(self, request_id):
        completion_time = self.request_monitor.get_completion_time(request_id=request_id)
        total_processing_time = self.request_monitor.get_total_processing_time(request_id=request_id)
        with open("{}/{}.csv".format(self.folder_location, self.active_filename), 'a') as f:
            writer = csv.writer(f)
            writer.writerow([request_id, completion_time, total_processing_time])

"""
Want to create a file for each run.
Each request has its own line that includes the completion time, and total processing time.

Each file can include multiple requests
Therefore the filename should be set in main or given to the outputwriter in the functions.

"""