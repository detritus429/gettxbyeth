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

description = F"""
Get ethereum transactions by sent ether value. 
"""

epilog = F"""
Have fun!
"""

eio_block_base = "https://etherscan.io/block/" 
eio_tx_base = "https://etherscan.io/tx/"

csv_columns = ("#","Value (ETH)","Value (wei)","Tx id","Tx link","Block number","Block link")
csv_delimiter = ";"

if __name__ == "__main__":
    
    print(F"For the list of options, run ./{os.path.basename(__file__)} -h")
    
    # parsing command line arguments
    parser = argparse.ArgumentParser(description=description, epilog=epilog) 
    configOptions = parser.add_argument_group("Config options")
    blockOptions = parser.add_argument_group("Block options")
    etherOptions = parser.add_argument_group("Ether options")
    outputOptions = parser.add_argument_group("Output options")
    # miscOptions = parser.add_argument_group("Miscellaneous options")
        # print latest block number and exit
        
    configOptions.add_argument("-c","--config-file",help="Use this config file (default: "+configfile+")")
    configOptions.add_argument("-p","--provider",help="Provider to use to connect to the chain")
    
    blockOptions.add_argument("-b","--block",help="Filter in an exact block (all other block options are ignored)", type=int)
    blockOptions.add_argument("-l","--latest", help="Filter in the last N blocks or only in the latest block if no value specified.", nargs='?', default=-1, metavar="N", type=int)
    blockOptions.add_argument("-v","--block-min", help="Minimum block number to filter in", type=int)
    blockOptions.add_argument("-n","--block-max", help="Maximum block number to filter in", type=int)
    # in the last x minute/hour/day
    
    etherOptions.add_argument("-s","--skip-zero", help="Don't list transactions with 0 ETH (other ether options still apply)", action='store_true')
    etherOptions.add_argument("-0","--zero-only", help="List transactions with 0 ETH only (other ether options are ignored)", action='store_true')
    etherOptions.add_argument("-E","--exact-eth", help="List txs only with this exact ETH value.")
    # etherOptions.add_argument("-W","--exact-wei", help="List txs only with this exact wei value")
    etherOptions.add_argument("-w","--eth-min", help="Minimum value in ETH to filter for", type=float)
    etherOptions.add_argument("-r","--eth-max", help="Maximum value in ETH to filter for", type=float)
    #etherOptions.add_argument("-q","--wei-min", help="Minimum ether value in wei to filter for", type=float)
    #etherOptions.add_argument("-e","--wei-max", help="Maximum ether value in wei to filter for", type=float)
    
    outputOptions.add_argument("-oT","--out-etherscanio", help="Generate etherscan.io link for the tx", action="store_true")
    outputOptions.add_argument("-oB","--out-block", help="Generate etherscan.io link for the block", action="store_true")
    #outputOptions.add_argument("-oH","--out-html", help="Generate html output", metavar="<filename>")
    #outputOptions.add_argument("-oF","--out-console", help="Save console output", metavar="<filename>")
    #outputOptions.add_argument("-oC","--out-csv", help="Save csv output", metavar="<filename>")
    #outputOptions.add_argument("-oA","--out-files", help="Save to every available file format", metavar="<filename>")
    
    args = parser.parse_args()
    
    p = args
    #print(p)
    #exit(-1)
    
    '''
    # parsing config file
    config = configparser.ConfigParser()    
    config.optionxform = str  # to preserve case of parameters in the config file
    
    # set defaults
    p.provider = ""
    p.block_min = None
    p.block_max = None
    p.latest = None
    p.eth_min = 0
    p.eth_max = None
    p.skip_zero = False
    p.zero_only = False
    
    
    # read from config file
    if args.config_file:
        configfile = args.config_file
        config.read(configfile)
        
        p.provider = config["infura"]["url"]  
        p.eth_min = config["ethrange"]["min"]
        p.eth_max = config["ethrange"]["max"]
        p.block_min = config["blockrange"]["min"]
        p.block_max = config["blockrange"]["max"] 
    
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
    '''
   
    ###### connecting to the chain    
    print(F"[*] Provider to use: ", end="")
    providerselect = [False,False,False,False] # http, ws, ipc, auto
    if len(p.provider)>0: 
        if p.provider[:4].lower() == "http":
            print(F"{p.provider} (treated as 'http' provider)")
            providerselect[0] = True
        elif p.provider[:2].lower() == "ws":
            print(F"{p.provider} (treated as 'ws' provider)")
            providerselect[1] = True
        else:
            print(F"{p.provider} (treated as 'ipc' provider)")
            providerselect[2] = True
    else:
        print("not specified, trying web3's auto connect")   
        providerselect[3] = True
        
    
    print("[*] Connecting...", end="")    
    if providerselect[0]: # http
        w3 = Web3(Web3.HTTPProvider(p.provider))        
    if providerselect[1]: # websocket
        w3 = Web3(Web3.WebsocketProvider(p.provider))   
    if providerselect[2]: # ipc
        w3 = Web3(Web3.IPCProvider(p.provider))         
    if providerselect[3]: # auto
        w3 = Web3()                                     
    
    
    if w3.isConnected():
        print(" success, we are now connected!",end="\n\n")
    else:
        print(" could not connect. Exiting...")
        exit(-1)
    
    # let every parameter be fine, set defaults if necessary
    latestblock = w3.eth.getBlock("latest")
    
    # block settings
    if p.block is not None:  # -b/--block
        blockmin = p.block
        blockmax = p.block
    elif p.latest != -1:    
        if p.latest is None:
            blockmin = latestblock.number
            blockmax = latestblock.number
        else:
            blockmin = latestblock.number - p.latest + 1
            blockmax = latestblock.number
    else:
        blockmin = int(p.block_min if p.block_min is not None else latestblock.number) 
        blockmax = int(p.block_max if p.block_max is not None else latestblock.number)
    
    # ether settings
    if p.zero_only:
        ethmin_wei = 0
        ethmax_wei = 0
    elif p.exact_eth is not None:
        ethmin_wei = w3.toWei(p.exact_eth, "ether")
        ethmax_wei = w3.toWei(p.exact_eth, "ether")
    else:
        ethmin_wei = w3.toWei(p.eth_min, "ether") if p.eth_min is not None else 0
        ethmax_wei = w3.toWei(p.eth_max, "ether") if p.eth_max is not None else None
    
    print(F"Latest block: {latestblock.number}")
    print(F"Block range: {blockmin} - {blockmax} ({blockmax-blockmin+1} {'blocks' if blockmax-blockmin>0 else 'block'})")
    print(F"Min ether: {w3.fromWei(ethmin_wei,'ether') } ({ethmin_wei} wei)")
    print(F"Max ether: {w3.fromWei(ethmax_wei,'ether') if ethmax_wei is not None else 'no upper limit'} ({ethmax_wei if ethmax_wei is not None else 'infinite'} wei)")
    if p.skip_zero:
        print("Not showing transactions with 0 ETH value") 
    
    
    start = datetime.now()
    print("")
    print("[*] Start @" + str(start),end="\n\n")
    
    sumofeth = 0
    numoftx = 0
    for blocknum in range(blockmin,blockmax+1):
        block = w3.eth.getBlock(blocknum)
        print(F"### Block no. {block.number} ###")
        print(F"[*] No. of txs in block: {len(block.transactions)}")
        if p.out_block:
            print(F"[*] {eio_block_base}{block.number}", end="\n\n")
        sumofethinblock = 0
        numoftxinblock = 0
        for tx in block.transactions:
            t = w3.eth.getTransaction(tx)
            if (t.value >= ethmin_wei and ethmax_wei is None) or \
               (t.value >= ethmin_wei and t.value <= ethmax_wei):
                   
                   if t.value==0 and p.skip_zero and p.zero_only is False:
                       continue
                        
                   print(F"{str(t.hash.hex())}: {w3.fromWei(t.value,'ether')} ETH ({t.value} wei)")
                   if p.out_etherscanio:
                       print(F"{eio_tx_base}{t.hash.hex()}", end="\n\n")                       
                       
                   sumofeth += t.value
                   numoftx += 1
                   sumofethinblock += t.value
                   numoftxinblock += 1
        print("")
        print(F"Number of filtered txs in this block: {numoftxinblock}")
        print(F"Sum transfered in these txs in this block: {w3.fromWei(sumofethinblock,'ether')} ETH ({sumofethinblock} wei)")
        print("")
        
    print("")
    print("------------------------------------------")
    print(F"Total number of filtered txs: {numoftx}")
    print(F"Total sum transfered in these txs: {w3.fromWei(sumofeth,'ether')} ETH ({sumofeth} wei)")
            
    end = datetime.now()
    print("")
    print("[*] End @"+str(end))
    print("[*] Elapsed time: " + str(end-start))


