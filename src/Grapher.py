import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta

class BarGrapher:

    def __init__(self):
        self.folder_location = "/home/house/AuctionFog/output/plots"
        self.run_folder = "/home/house/AuctionFog/output/runs"
        self.run_headers = ['completion_time', 'total_processing_time']

    def create_bar_graph(self, run_filename, graph_filename:None):
        if graph_filename == None:
            graph_filename = run_filename
        [avg_completion_time, avg_total_processing_time] = self.get_data(run_filename)
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.set_ylabel('Time [sec]')
        times = [avg_completion_time.total_seconds(), avg_total_processing_time.total_seconds()]
        ax.bar(["Completion Time", "Total Processing Time"], times)
        plt.savefig("/home/house/AuctionFog/output/plots/{}.png".format(graph_filename), bbox_inches='tight')

    """
        Reads the output file and returns 
        the average completion time and average total processing time for the run
        as timedelta objects
    """
    def get_data(self, run_filename):
        #Nice with average if we are running dissimilar requests
        avg_completion_time = timedelta() 
        avg_total_processing_time = timedelta()
        with open("{}/{}.csv".format(self.run_folder,run_filename), 'r') as f:
            reader = csv.reader(f)
            next(reader)
            i = 0
            for line in reader:
                completion_time_str = line[1]
                completion_time_d_time =  datetime.strptime(completion_time_str,"%H:%M:%S.%f")
                completion_time_t_delta = timedelta(
                    hours=completion_time_d_time.hour, 
                    minutes=completion_time_d_time.minute, 
                    seconds=completion_time_d_time.second, 
                    microseconds=completion_time_d_time.microsecond)
                avg_completion_time = (avg_completion_time*i+completion_time_t_delta)/(i+1)
                total_processing_time_str = line[2]
                total_processing_time_d_time =  datetime.strptime(total_processing_time_str,"%H:%M:%S.%f")
                total_processing_time_t_delta = timedelta(
                    hours=total_processing_time_d_time.hour, 
                    minutes=total_processing_time_d_time.minute, 
                    seconds=total_processing_time_d_time.second, 
                    microseconds=total_processing_time_d_time.microsecond)
                avg_total_processing_time = (avg_total_processing_time*i+total_processing_time_t_delta)/(i+1)
                i+=1
        return [avg_completion_time, avg_total_processing_time]