#!/usr/bin/env python3

import configparser
import argparse
import os
from types import SimpleNamespace
from datetime import datetime

from web3 import Web3

configfile = "config.ini"
p = SimpleNamespace() # parameters to work with
                      # populate from config file then overwrite from command line

if __name__ == "__main__":
    
    start = datetime.now()
    print("[*] Start @" + str(start))
    
    print("#### Get ethereum transactions by sent ether value ####")
    print("For the list of options, run ./" + os.path.basename(__file__) + " --help")
    print("")
    
    # parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config-file",help="Use this config file (default: "+configfile+")")
    parser.add_argument("-w","--eth-min", help="Minimum ether value to filter for (default: 0)")
    parser.add_argument("-r","--eth-max", help="Maximum ether value to filter for (default: infinite)")
    parser.add_argument("-v","--block-min", help="Minimum block number to filter for (default: latest)")
    parser.add_argument("-n","--block-max", help="Maximum block number to filter for (default: latest)")
    args = parser.parse_args()
    
    # parsing config file
    config = configparser.ConfigParser()    
    config.optionxform = str  # to preserve case of parameters in the config file
    
    if args.config_file:
        configfile = args.config_file
    
    config.read(configfile)
    
    if config["infura"]["id"] == "":
        print("Infura id is missing, please edit the '" + configfile + "' configuration file.")
        exit(-1)
    
    infuraurl = config["infura"]["url"] + config["infura"]["id"]
   
    p.provider = infuraurl
    p.account = config["DEFAULT"]["account"]
    p.eth_min = config["ethrange"]["min"]
    p.eth_max = config["ethrange"]["max"]
    
    # overwrite settings from command line
    if args.eth_min:
        p.eth_min = args.eth_min
    if args.eth_max:
        p.eth_max = args.eth_max
    
    ###### connecting to the chain
    w3 = Web3(Web3.HTTPProvider(p.provider))
    if w3.isConnected():
        print("[*] connected to %s" % p.provider)
    else:
        print("[!] not connected, exiting")
        exit(-1)
    
    # get info from chain
    print("Account: " + p.account)
    # print("Balance: " + str(w3.fromWei(w3.eth.getBalance(account),"ether")) + " ETH")
    
    latestblock = w3.eth.getBlock("latest")
    
    print("Block no.: " + str(latestblock.number))
    print("No. of tx in block: " + str(len(latestblock.transactions)))
    print("Min eth: " + str(p.eth_min) + " ETH (" + str(w3.toWei(p.eth_min, "ether")) + " wei)")
    print("Max eth: " + str(p.eth_max) + " ETH (" + str(w3.toWei(p.eth_max, "ether")) + " wei)")
    
    for tx in latestblock.transactions:
        t = w3.eth.getTransaction(tx)
        if t.value > w3.toWei(p.eth_min, "ether") and t.value < w3.toWei(p.eth_max, "ether"):
            print(str(t.hash.hex()) + ": ", end="")
            print(str(t.value))
    end = datetime.now()
    print("[*] End @"+str(end))
    print("[*] Elapsed time: " + str(end-start))


