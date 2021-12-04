from datetime import datetime, timedelta

class RequestMonitor:

    def __init__(self):
        self.req_id_index = 0
        self.requests = {}

    #Return a request id to be used, ads the new request to active requests.
    def get_request_id(self):
        request_id = self.req_id_index
        self.req_id_index += 1
        self.requests[request_id] = self.Request(request_id)
        return request_id
    
    def start_request(self, request_id):
        self.requests[request_id].start()
    
    def start_processing(self, request_id, node_id):
        print("RequestMonitor: {} has started to process request {}.".format(node_id, request_id))
        self.requests[request_id].process_start(node_id)
    
    def complete_processing(self, request_id, node_id):
        print("RequestMonitor: {} has completed the processing of request {}.".format(node_id, request_id))
        self.requests[request_id].process_complete(node_id)
    
    #Returns a timedelta of the complete processing time for all currently finished Nodes
    def get_total_processing_time(self, request_id):
        return self.requests[request_id].total_time
    
    #Returns timedelta object that represents the time from when the request turned active to the first completed job
    def get_completion_time(self, request_id):
        return self.requests[request_id].first_completion - self.requests[request_id].start_time

    def get_processing_times(self, request_id):
        return self.requests[request_id].get_processing_times()

    class Request:

        def __init__(self, request_id):
            self.request_id = request_id

            self.start_time = None #Time when request has turned active
            self.first_completion = None #Time for first completed processing
            self.total_time = timedelta() #Total time spent processing, only accounts for jobs that are finished

            self.nodes = {} #Set of Nodes that are/have processed this request with start and completion times
        
        def start(self):
            self.start_time = datetime.now()
        
        #Called when Node starts processing this request
        def process_start(self, node_id):
            process_start_time = datetime.now()
            self.nodes[node_id] = {}
            self.nodes[node_id]["start_t"] = process_start_time

        #Called when Node completes processing this request
        def process_complete(self, node_id):
            completion_time = datetime.now()
            if self.first_completion == None:
                self.first_completion = completion_time
            
            self.nodes[node_id]["completion_t"] = completion_time
            self.recalculate_totaltime(node_id)
        
        #Adds Node's processing time to the total processing time
        def recalculate_totaltime(self, node_id):
            n_start = self.nodes[node_id]["start_t"]
            n_complete =self.nodes[node_id]["completion_t"]
            t_delta = n_complete-n_start
            self.total_time += t_delta
        
        def get_processing_times(self):
            return self.nodes

