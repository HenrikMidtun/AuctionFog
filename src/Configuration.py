
class Catalogue:
    services = {
        "A":{"asking_price":50, "std_process_t":3},
        "B":{"asking_price":40, "std_process_t":3}, 
        "C":{"asking_price":50, "std_process_t":3}
    }

class AuctionConfig:
    auction_period = 0.1
    joining_period = 0.1

class ProcessingConfig:
    processing_constant = 0.5

class BattistoniConfig:
    grace_constant = 2 #should be time it takes to find out that the service wont be, e.g., max processing time ~ 2*T_0