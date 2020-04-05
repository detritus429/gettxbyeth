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
    
    print("#### Get ethereum transactions by sent ether value ####")
    print("For the list of options, run ./" + os.path.basename(__file__) + " --help")
    print("")
    
    # parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config-file",help="Use this config file (default: "+configfile+")")
    parser.add_argument("-p","--provider",help="Provider to use to connect to the chain")
    parser.add_argument("-w","--eth-min", help="Minimum ether value to filter for (default: 0)")
    parser.add_argument("-r","--eth-max", help="Maximum ether value to filter for (default: infinite)")
    #parser.add_argument("-l","--latest", help="When set with no parameter, the latest block will be analyzed
    parser.add_argument("-v","--block-min", help="Minimum block number to filter for (default: latest)")
    parser.add_argument("-n","--block-max", help="Maximum block number to filter for (default: latest)")
    args = parser.parse_args()
    
    # parsing config file
    config = configparser.ConfigParser()    
    config.optionxform = str  # to preserve case of parameters in the config file
    
    if args.config_file:
        configfile = args.config_file
        config.read(configfile)
        
        p.provider = config["infura"]["url"]  
        p.eth_min = config["ethrange"]["min"] if config["ethrange"]["min"] else 0
        p.eth_max = config["ethrange"]["max"] if config["ethrange"]["max"] else None   # 'None' translates to "infinity" 
        p.block_min = config["blockrange"]["min"] if config["blockrange"]["min"] else None # 'None' translates to "latest"
        p.block_max = config["blockrange"]["max"] if config["blockrange"]["max"] else None # 'None' translates to "latest"
    
    
    
    # overwrite settings from command line
    if args.provider:
        p.provider = args.provider
    if args.eth_min:
        p.eth_min = args.eth_min
    if args.eth_max:
        p.eth_max = args.eth_max
    if args.block_min:
        p.block_min = args.block_min
    if args.block_max:
        p.block_max = args.block_max
   
    ###### connecting to the chain
    
    print(F"[*] Provider to use: ", end="")
    providerselect = [False,False,False,False] # http, ws, ipc, auto
    if hasattr(p,'provider') and len(p.provider)>0: 
        if p.provider[:4].lower() == "http":
            print(F"{p.provider} (treat as 'http' provider)")
            providerselect[0] = True
        elif p.provider[:2].lower() == "ws":
            print(F"{p.provider} (treat as 'ws' provider)")
            providerselect[1] = True
        else:
            print(F"{p.provider} (treat as 'ipc' provider)")
            providerselect[2] = True
    else:
        print("not set, trying web3's auto connect")   
        providerselect[3] = True
        
    
    print("[*] Connecting...")    
    if providerselect[0]: # http
        w3 = Web3(Web3.HTTPProvider(p.provider))        
    if providerselect[1]: # websocket
        w3 = Web3(Web3.WebsocketProvider(p.provider))   
    if providerselect[2]: # ipc
        w3 = Web3(Web3.IPCProvider(p.provider))         
    if providerselect[3]: # auto
        w3 = Web3()                                     
    
    
    if w3.isConnected():
        print(F"[*] Successful, connected to {p.provider}")
    else:
        print("[!] Not connected, exiting...")
        exit(-1)
    
    # let every parameter be fine
    latestblock = w3.eth.getBlock("latest")
    ethmin_wei = w3.toWei(p.eth_min, "ether")
    ethmax_wei = None if p.eth_max is None else w3.toWei(p.eth_max, "ether")
    blockmin = int(p.block_min if p.block_min else latestblock.number)
    blockmax = int(p.block_max if p.block_max else latestblock.number)
   
   
    
    print(F"Latest block: {latestblock.number}")
    print(F"Block range: {blockmin} - {blockmax} ({blockmax-blockmin+1} {'blocks' if blockmax-blockmin>0 else 'block'})")
    print(F"Min ether: {p.eth_min} ({ethmin_wei} wei)")
    print(F"Max ether: {p.eth_max if p.eth_max else 'no upper limit'} ({ethmax_wei if ethmax_wei else 'infinite'} wei)")
    
    start = datetime.now()
    print("")
    print("[*] Start @" + str(start),end="\n\n")
    
    sumofeth = 0
    numoftx = 0
    for blocknum in range(blockmin,blockmax+1):
        block = w3.eth.getBlock(blocknum)
        print(F"### Block no. {block.number} ###")
        print(F"[*] No. of tx in block: {len(block.transactions)}")
        for tx in block.transactions:
            t = w3.eth.getTransaction(tx)
            if (t.value >= ethmin_wei and not p.eth_max) or \
               (t.value >= ethmin_wei and t.value <= ethmax_wei):
                   print(F"{str(t.hash.hex())}: {w3.fromWei(t.value,'ether')} ETH ({t.value} wei)")
                   sumofeth += t.value
                   numoftx += 1
        print("")
    
    print("")
    print(F"Number of filtered tx: {numoftx}")
    print(F"Sum transfered in these transactions: {w3.fromWei(sumofeth,'ether')} ETH ({sumofeth} wei)")
            
    end = datetime.now()
    print("")
    print("[*] End @"+str(end))
    print("[*] Elapsed time: " + str(end-start))


