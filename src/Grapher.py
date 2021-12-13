import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
import numpy as np

class BarGrapher:

    def __init__(self):
        self.folder_location = "/home/house/AuctionFog/output/plots"
        self.run_folder = "/home/house/AuctionFog/output/runs"
        self.run_headers = ['completion_time', 'total_processing_time']

    def graph_completion_time(self, run_filename, graph_filename=None, subtitle=None):
        if graph_filename == None:
            graph_filename = run_filename
        data_t_delta = self.get_data(run_filename)
        plot_data = []
        for k,v in data_t_delta.items():
            completion_time = v["avg_completion_time"].total_seconds()
            plot_data.append(completion_time)
        fig, ax = plt.subplots()
        ax.set_ylabel('Time [sec]')
        bar_plot = ax.bar(["Auction", "Random Choice", "Modified Battistoni"], plot_data)
        bar_plot[0].set_color("#82B366")
        bar_plot[1].set_color("#D6B656")
        bar_plot[2].set_color("#B85450")
        mid = (fig.subplotpars.right + fig.subplotpars.left)/2
        plt.suptitle("Completion Times", x=mid)
        if subtitle != None:
            ax.set_title(subtitle)

        plt.savefig("/home/house/AuctionFog/output/plots/{}_completiontime.png".format(graph_filename), bbox_inches='tight')

    def graph_processing_time(self, run_filename, graph_filename:None, subtitle=None):
        if graph_filename == None:
            graph_filename = run_filename
        data_t_delta = self.get_data(run_filename)
        plot_data = []
        for k,v in data_t_delta.items():
            processing_time = v["avg_processing_time"].total_seconds()
            plot_data.append(processing_time)
        fig, ax = plt.subplots()
        ax.set_ylabel('Time [sec]')
        bar_plot = ax.bar(["Auction", "Random Choice", "Modified Battistoni"], plot_data)
        bar_plot[0].set_color("#82B366")
        bar_plot[1].set_color("#D6B656")
        bar_plot[2].set_color("#B85450")
        mid = (fig.subplotpars.right + fig.subplotpars.left)/2
        plt.suptitle("Processing Times", x=mid)
        if subtitle != None:
            ax.set_title(subtitle)

        plt.savefig("/home/house/AuctionFog/output/plots/{}_processingtime.png".format(graph_filename), bbox_inches='tight')
    """
        Reads the output file and returns 
        the average completion time and average total processing time for the run
        as timedelta objects

        data = {"auction": "avg_total_processing_time": 10.4, "avg_completion_time": 2.1}
    """
    def get_data(self, run_filename):
        #Nice with average if we are running dissimilar requests
        data = {
            "auction":{
                "avg_completion_time": timedelta(),
                "avg_processing_time": timedelta()
                },
            "choice":{
                "avg_completion_time": timedelta(),
                "avg_processing_time": timedelta()
                },
            "battistoni":{
                "avg_completion_time": timedelta(),
                "avg_processing_time": timedelta()
                }
            }
        with open("{}/{}.csv".format(self.run_folder,run_filename), 'r') as f:
            reader = csv.reader(f)
            next(reader)
            counter = {"auction": 0, "choice": 0, "battistoni": 0}
            for line in reader:
                n_type = line[0]
                completion_time_str = line[2]
                completion_time_d_time =  datetime.strptime(completion_time_str,"%H:%M:%S.%f")
                completion_time_t_delta = timedelta(
                    hours=completion_time_d_time.hour, 
                    minutes=completion_time_d_time.minute, 
                    seconds=completion_time_d_time.second, 
                    microseconds=completion_time_d_time.microsecond)
                data[n_type]["avg_completion_time"] = (data[n_type]["avg_completion_time"]*counter[n_type]+completion_time_t_delta)/(counter[n_type]+1)
                total_processing_time_str = line[3]
                total_processing_time_d_time =  datetime.strptime(total_processing_time_str,"%H:%M:%S.%f")
                total_processing_time_t_delta = timedelta(
                    hours=total_processing_time_d_time.hour, 
                    minutes=total_processing_time_d_time.minute, 
                    seconds=total_processing_time_d_time.second, 
                    microseconds=total_processing_time_d_time.microsecond)
                data[n_type]["avg_processing_time"] = (data[n_type]["avg_processing_time"]*counter[n_type]+total_processing_time_t_delta)/(counter[n_type]+1)
                counter[n_type] = counter[n_type]+1
        return data