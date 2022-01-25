# AuctionFog
Master thesis work in fog computing, MQTT and auctioning mechanisms.

Setup:
Install dependencies with pip
1. Enter the repository
2. Create virtual environment of choice (pipenv, venv, ...)
3. Install dependencies through requirements.txt

Example:
```bat
cd AuctionFog
python3 -m pipenv shell
pip install -r requirements.txt
```

Run:
From the root directory, run the main file with Python.

The main file contains code to run a simulation for the auction, random choice, and modified Battistoni implementations on the default network.
The results are outputted into a default file, outputs/sessions/default.csv

Modify:
Change the parameters of each run in src/configuration.py or change network topology in src/main.py

The mean bid size, standard deviation of bid size, asking price of requests, and standard processing time can be set in the configuration file.

The network topology is structured as a dictionary {"n_id": ["c_id"]. Each Node is given an id and a Node's neighbours are given as a list of ids.
