
class Catalogue:
    services = {
        "A":{"asking_price":50, "std_process_t":3},
        "B":{"asking_price":40, "std_process_t":3}, 
        "C":{"asking_price":50, "std_process_t":3}
    }

class AuctionConfig:
    auction_period = 0.3
    joining_period = 0.2

class ProcessingConfig:
    processing_constant = 0.5