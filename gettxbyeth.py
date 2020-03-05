#!/usr/bin/env python3

import configparser
from web3 import Web3



configfile = "config_dev.ini"
eththreshold = 1

if __name__ == "__main__":
    
    print("#### Get ethereum transactions by sent ether value ####")
    print("")
    
    config = configparser.ConfigParser()    
    config.optionxform = str
    
    config.read(configfile)
    
    if config["infura"]["id"] == "":
        print("Infura id is missing, please edit the " + configfile + " file.")
        exit(-1)
    
    infuraurl = config["infura"]["url"] + config["infura"]["id"]
    provider = infuraurl
    
    account = config["DEFAULT"]["account"]
    
    
    
    ###### connecting to the chain
    w3 = Web3(Web3.HTTPProvider(provider))
    if w3.isConnected():
        print("[*] connected to %s" % provider)
    else:
        print("[!] not connected, exiting")
        exit(-1)
    
    # get info from chain
    print("Account: " + account)
    # print("Balance: " + str(w3.fromWei(w3.eth.getBalance(account),"ether")) + " ETH")
    
    latestblock = w3.eth.getBlock("latest")
    
    print("Block no.:" + str(latestblock.number))
    print("No. of tx in block: " + str(len(latestblock.transactions)))
    print("Threshold: " + str(eththreshold) + " ETH (" + str(w3.toWei(eththreshold, "ether")) + " wei)")
    
    for tx in latestblock.transactions:
        t = w3.eth.getTransaction(tx)
        if t.value > w3.toWei(eththreshold, "ether"):
            print(str(t.hash.hex()) + ": ", end="")
            print(str(t.value))
