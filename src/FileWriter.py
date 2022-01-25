import csv
from RequestMonitor import RequestMonitor
from datetime import datetime, timedelta
import statistics


"""
Creates a file for each session.
Each run has its own line that includes the completion time, and total processing time.
Each file includes multiple runs
Each line includes the assigment method that was used for the run.
"""
class SessionWriter:

    def __init__(self, request_monitor:RequestMonitor):
        self.folder_location = "./output/sessions"
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

class AnalyticsWriter:

    def __init__(self):
        self.session_folder = "./output/sessions"
        self.analytics_folder = "./output/analytics"

    def findMinMaxSDValuesForSession(self, session_file=None):

        with open("{}/{}.csv".format(self.session_folder, session_file), 'r') as f:
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
        avg_pt_auction = statistics.mean(data["auction"]["pt"])
        avg_ct_auction = statistics.mean(data["auction"]["ct"])
        avg_pt_choice = statistics.mean(data["choice"]["pt"])
        avg_ct_choice = statistics.mean(data["choice"]["ct"])
        avg_pt_batt = statistics.mean(data["battistoni"]["pt"])
        avg_ct_batt = statistics.mean(data["battistoni"]["ct"])

        results = {
                "auction": {
                    "max_pt":max_pt_auction,
                    "max_ct":max_ct_auction,
                    "min_pt":min_pt_auction,
                    "min_ct":min_ct_auction,
                    "sd_pt":sd_pt_auction,
                    "sd_ct":sd_ct_auction,
                    "avg_pt":avg_pt_auction,
                    "avg_ct":avg_ct_auction
                },
                "choice": {
                    "max_pt":max_pt_choice,
                    "max_ct":max_ct_choice,
                    "min_pt":min_pt_choice,
                    "min_ct":min_ct_choice,
                    "sd_pt":sd_pt_choice,
                    "sd_ct":sd_ct_choice,
                    "avg_pt":avg_pt_choice,
                    "avg_ct":avg_ct_choice
                },
                "battistoni": {
                    "max_pt":max_pt_batt,
                    "max_ct":max_ct_batt,
                    "min_pt":min_pt_batt,
                    "min_ct":min_ct_batt,
                    "sd_pt":sd_pt_batt,
                    "sd_ct":sd_ct_batt,
                    "avg_pt":avg_pt_batt,
                    "avg_ct":avg_ct_batt
                }
            }
        return results

    def write_analytics_file(self, filename, sessions:dict, variable):
        folder_path = "./output/analytics"
        headers = ["var", "val", "type", "avg_pt", "max_pt", "min_pt", "sd_pt", "avg_ct", "max_ct", "min_ct", "sd_ct"]

        with open("{}/{}.csv".format(folder_path,filename), "w") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for value, session_file in sessions.items():
                data = self.findMinMaxSDValuesForSession(session_file=session_file)

                for k,v in data.items():
                    print(k)
                    print(v)
                    row = [variable, value, k, v["avg_pt"], v["max_pt"], v["min_pt"], v["sd_pt"], v["avg_ct"], v["max_ct"], v["min_ct"], v["sd_ct"]]
                    writer.writerow(row)
