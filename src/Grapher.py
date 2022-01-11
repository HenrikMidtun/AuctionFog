import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
import numpy as np
import statistics

class BarGrapher:

    def __init__(self):
        self.folder_location = "/home/house/AuctionFog/output/plots"
        self.session_folder = "/home/house/AuctionFog/output/sessions"
        self.run_headers = ['completion_time', 'total_processing_time']

    """
        Creats a grouped bar chart of multiple runs. 
        The run sources and groups must be ordered in the same way for labels to be correct.

        EX.    run_sources = [filename_30,filename_50,filename_70]
               groups = [30,50,70]
    """
    def graph_comparison_compl_t(self, session_sources, graph_filename, groups, label, subtitle=None):
        plot_data = [[],[],[]]
        for session_file in session_sources:
            data_t_delta = self.get_data(session_file)
            for k,v in data_t_delta.items():
                completion_time = v["avg_completion_time"].total_seconds()
                if k == "auction":
                    plot_data[0].append(completion_time)
                elif k == "choice":
                    plot_data[1].append(completion_time)
                elif k == "battistoni":
                    plot_data[2].append(completion_time)
        barWidth = 0.25
        fig, ax = plt.subplots(figsize =(8, 6))
        bar1 = np.arange(len(plot_data[0]))
        bar2 = [x + barWidth for x in bar1]
        bar3 = [x + barWidth for x in bar2]

        plt.bar(bar1, plot_data[0], color ="#82B366", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Auction')
        plt.bar(bar2, plot_data[1], color ="#D6B656", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Random Choice')
        plt.bar(bar3, plot_data[2], color ="#B85450", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Modified Battistoni')

        mid = (fig.subplotpars.right + fig.subplotpars.left)/2
        plt.suptitle("Completion Times", x=mid, size='xx-large', weight="bold")
        if subtitle != None:
            ax.set_title(subtitle, style="italic")

        plt.xlabel(label, fontweight ='bold', fontsize = 13, labelpad=15)
        plt.ylabel('Time [sec]', fontweight ='bold', fontsize = 13, labelpad=15)
        plt.xticks([r + barWidth for r in range(len(plot_data[0]))], groups)

        plt.legend(bbox_to_anchor= (1.02, 1), loc="upper left")
        plt.savefig("/home/house/AuctionFog/output/plots/compare_{}_completiontime.png".format(graph_filename), bbox_inches='tight')

    def graph_comparison_proc_t(self, session_sources, graph_filename, groups, label, subtitle=None):
        plot_data = [[],[],[]]
        for session_file in session_sources:
            data_t_delta = self.get_data(session_file)
            for k,v in data_t_delta.items():
                processing_time = v["avg_processing_time"].total_seconds()
                if k == "auction":
                    plot_data[0].append(processing_time)
                elif k == "choice":
                    plot_data[1].append(processing_time)
                elif k == "battistoni":
                    plot_data[2].append(processing_time)
        barWidth = 0.25
        fig, ax = plt.subplots(figsize =(8, 6))
        bar1 = np.arange(len(plot_data[0]))
        bar2 = [x + barWidth for x in bar1]
        bar3 = [x + barWidth for x in bar2]

        plt.bar(bar1, plot_data[0], color ="#82B366", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Auction')
        plt.bar(bar2, plot_data[1], color ="#D6B656", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Random Choice')
        plt.bar(bar3, plot_data[2], color ="#B85450", width = barWidth, edgecolor ="black", linewidth=0.5, label ='Modified Battistoni')

        mid = (fig.subplotpars.right + fig.subplotpars.left)/2
        plt.suptitle("Processing Times", x=mid, size='xx-large', weight="bold")
        if subtitle != None:
            ax.set_title(subtitle, style="italic")

        plt.xlabel(label, fontweight ='bold', fontsize = 13, labelpad=15)
        plt.ylabel('Time [sec]', fontweight ='bold', fontsize = 13, labelpad=15)
        plt.xticks([r + barWidth for r in range(len(plot_data[0]))], groups)

        plt.legend(bbox_to_anchor= (1.02, 1), loc="upper left")
        plt.savefig("/home/house/AuctionFog/output/plots/compare_{}_processingtime.png".format(graph_filename), bbox_inches='tight')

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
        with open("{}/{}.csv".format(self.session_folder,run_filename), 'r') as f:
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


def findMinMaxSDValuesForSession(session_file=None):
    session_folder = "/home/house/AuctionFog/output/sessions"

    with open("{}/{}.csv".format(session_folder, session_file), 'r') as f:
        reader = csv.reader(f)
        next(reader)
        data = {
            "auction": {
                "pt":[],
                "ct":[]
            },
            "choice": {
                "pt":[],
                "ct":[]
            },
            "battistoni": {
                "pt":[],
                "ct":[]
            }
        }
        for line in reader:
            n_type = line[0]

            completion_time_str = line[2]
            completion_time_datetime_obj =  datetime.strptime(completion_time_str,"%H:%M:%S.%f")
            completion_time_timedelta_obj = timedelta(
                hours=completion_time_datetime_obj.hour, 
                minutes=completion_time_datetime_obj.minute, 
                seconds=completion_time_datetime_obj.second, 
                microseconds=completion_time_datetime_obj.microsecond)
            completion_time_seconds = completion_time_timedelta_obj.total_seconds()
            data[n_type]["ct"].append(completion_time_seconds)
            total_processing_time_str = line[3]
            total_processing_time_datetime_obj =  datetime.strptime(total_processing_time_str,"%H:%M:%S.%f")
            total_processing_time_timedelta_obj = timedelta(
                hours=total_processing_time_datetime_obj.hour, 
                minutes=total_processing_time_datetime_obj.minute, 
                seconds=total_processing_time_datetime_obj.second, 
                microseconds=total_processing_time_datetime_obj.microsecond)
            total_processing_time_seconds = total_processing_time_timedelta_obj.total_seconds()
            data[n_type]["pt"].append(total_processing_time_seconds)
    max_pt_auction = max(data["auction"]["pt"])
    max_pt_choice = max(data["choice"]["pt"])
    max_pt_batt = max(data["battistoni"]["pt"])
    min_pt_auction = min(data["auction"]["pt"])
    min_pt_choice = min(data["choice"]["pt"])
    min_pt_batt = min(data["battistoni"]["pt"])
    max_ct_auction = max(data["auction"]["ct"])
    max_ct_choice = max(data["choice"]["ct"])
    max_ct_batt = max(data["battistoni"]["ct"])
    min_ct_auction = min(data["auction"]["ct"])
    min_ct_choice = min(data["choice"]["ct"])
    min_ct_batt = min(data["battistoni"]["ct"])
    sd_pt_auction = statistics.pstdev(data["auction"]["pt"])
    sd_ct_auction = statistics.pstdev(data["auction"]["ct"])
    sd_pt_choice = statistics.pstdev(data["choice"]["pt"])
    sd_ct_choice = statistics.pstdev(data["choice"]["ct"])
    sd_pt_batt = statistics.pstdev(data["battistoni"]["pt"])
    sd_ct_batt = statistics.pstdev(data["battistoni"]["ct"])
    results = {
            "auction": {
                "max_pt":max_pt_auction,
                "max_ct":max_ct_auction,
                "min_pt":min_pt_auction,
                "min_ct":min_ct_auction,
                "sd_pt":sd_pt_auction,
                "sd_ct":sd_ct_auction
            },
            "choice": {
                "max_pt":max_pt_choice,
                "max_ct":max_ct_choice,
                "min_pt":min_pt_choice,
                "min_ct":min_ct_choice,
                "sd_pt":sd_pt_choice,
                "sd_ct":sd_ct_choice
            },
            "battistoni": {
                "max_pt":max_pt_batt,
                "max_ct":max_ct_batt,
                "min_pt":min_pt_batt,
                "min_ct":min_ct_batt,
                "sd_pt":sd_pt_batt,
                "sd_ct":sd_ct_batt
            }
        }
    return results

print(findMinMaxSDValuesForSession("bids/Net1Runs500Meanbid30SD20"))
