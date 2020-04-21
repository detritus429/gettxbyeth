#!/usr/bin/env python3

import configparser
import argparse
import os
from types import SimpleNamespace
from datetime import datetime

from web3 import Web3

f_console = None
f_csv = None
f_html = None

configfile = "config.ini"
p = SimpleNamespace() # parameters to work with
                      # populate from config file then overwrite from command line

def write_to_console(line, end="\n"):
    """Write line to console and the same to file if necessary"""
    
    print(line,end=end)
    
    if f_console is not None:
        print(line, file=f_console, end=end, flush=True)

csv_columns = ("#","#b","Value (ETH)","Value (wei)","Tx id","Tx link","Block number","Block link")
csv_delimiter = ";"

def getCSVLine(data):
    """Data is a tuple of (n,nb,value_wei,tx_id,block_number)."""
    """
        n = data[0]  # number in all
        nb = data[1]  # number in block
        eth = w3.fromWei(wei,'ether')
        wei = data[2]
        tx = data[1]
        txlink = getTxLink(tx)
        block = data[2]
        blockLink = getBlockLink(block)
    """
   
    # csv_columns = ("#","#b","Value (ETH)","Value (wei)","Tx id","Tx link","Block number","Block link")
    #  0 1    2         3       4
    # (n,nb,value_wei,tx_id,block_number)
    return F"{data[0]}{csv_delimiter}\
{data[1]}{csv_delimiter}\
{w3.fromWei(data[2],'ether')}{csv_delimiter}\
{data[2]}{csv_delimiter}\
{data[3]}{csv_delimiter}\
{getTxLink(data[3])}{csv_delimiter}\
{data[4]}{csv_delimiter}\
{getBlockLink(data[4])}"  # end of getCSVLine

# html start
#                    0               1           2       3        4         5
# addHtmlStart((latestblock.number,blockmin,blockmax,ethmin_wei,ethmax_wei,start))
def addHtmlStart(settings):
    latestblock = settings[0]
    blockmin = settings[1]
    blockmax = settings[2]
    ethmin_wei = settings[3] 
    ethmax_wei = settings[4] if settings[4] is not None else "infinite"
    start = settings[5]
    ethmin = w3.fromWei(ethmin_wei,'ether')
    ethmax = w3.fromWei(ethmax_wei,'ether') if settings[4] is not None else "infinite"
    
    return F"""
<html><title>ETH range: {ethmin} - {ethmax} | Blockrange: {blockmin}-{blockmax}</title><body>
<h1>Settings</h1>

<table>
<tr>
    <td>Latest block:</td>
    <td>{latestblock}</td>
</tr>
<tr>
    <td>Block range:</td>
    <td>{blockmin} - {blockmax} ({blockmax-blockmin+1} {'blocks' if blockmax-blockmin>0 else 'block'})</td>
</tr>
<tr>
    <td>ETH range:</td>
    <td>{ethmin}-{ethmax} ETH ({ethmin_wei}-{ethmax_wei} wei) </td>
</tr>
</table>

<hr/>
Started @{start} <br/><br/>
<table>
<tr>
<td>#</td>
<td># in block</td>
<td>Value (eth)</td>
<td>Value (wei)</td>
<td>tx hash</td>
<td>block number</td>
<tr>
"""
#            0       1               2     3      4
# data = (numoftx,numoftxinblock,t.value,txstr,block.number)   # (n,nb,value_wei,tx_id,block_number)
def addHtmlLine(data):
    return F"""
<tr>
    <td>{data[0]}</td>
    <td>{data[1]}</td>
    <td>{w3.fromWei(data[2],'ether')}</td>
    <td>{data[2]}</td>
    <td><a href={getTxLink(data[3])}>{data[3]}</a></td>
    <td><a href={getBlockLink(data[4])}>{data[4]}</a></td>
<tr>
"""

def addHtmlBlockSummary(data):
    return F"""
    
    
    
    """
#               0       1           2       3
# results = (numoftx, sumofeth, str(end),str(end-start))
def addHtmlEnd(data):
    return F"""</table>
<br/>
End: {data[2]}<br/>
Elapsed time: {data[3]}
<hr/>
<table>
<tr>
    <td> Total number of txs:</td>
    <td> {data[0]}</td>
</tr>
<tr>
    <td> Total ETHs transfered:</td>
    <td>{w3.fromWei(sumofeth,'ether')} ETH ({sumofeth} wei)</td>
</tr>

</table>
</body></html>
"""
# html end



eio_block_base = "https://etherscan.io/block/" 
eio_tx_base = "https://etherscan.io/tx/"

def getTxLink(tx):
    """Returns the etherscan.io link of the tx"""
    return F"{eio_tx_base}{tx}"

def getBlockLink(b):
    """Returns the etherscan.io link of the block number"""
    return F"{eio_block_base}{b}"

# big strings
description = F"""
Get ethereum transactions by sent ether value. 
"""

epilog = F"""
Have fun!
"""

if __name__ == "__main__":
    
    print(F"For the list of options, run ./{os.path.basename(__file__)} -h")
    
    # parsing command line arguments
    parser = argparse.ArgumentParser(description=description, epilog=epilog) 
    configOptions = parser.add_argument_group("Config options")
    blockOptions = parser.add_argument_group("Block options")
    etherOptions = parser.add_argument_group("Ether options")
    outputOptions = parser.add_argument_group("Output options")
        
    #configOptions.add_argument("-c","--config-file",help="Use this config file (default: "+configfile+")")
    configOptions.add_argument("-p","--provider",help="Provider to use to connect to the chain")
    
    blockOptions.add_argument("-b","--block",help="Filter in this exact block (all other block options are ignored)", type=int)
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
    
    outputOptions.add_argument("-oT","--out-txlink", help="Generate etherscan.io link for the tx", action="store_true")
    outputOptions.add_argument("-oB","--out-blocklink", help="Generate etherscan.io link for the block", action="store_true")
    outputOptions.add_argument("-oH","--out-html", help="Generate html output", metavar="<filename>")
    outputOptions.add_argument("-oF","--out-console", help="Save console output", metavar="<filename>")
    outputOptions.add_argument("-oC","--out-csv", help="Save csv output", metavar="<filename>")
    outputOptions.add_argument("-oA","--out-files", help="Save to every available file format", metavar="<filename>")
    
    args = parser.parse_args()
    
    p = args
    # print(p)
    # exit(-1)
    
    # output files
    if p.out_files is not None:
        p.out_console = p.out_files + ".txt"
        p.out_csv = p.out_files + ".csv"
        p.out_html = p.out_files + ".html"
    
    if p.out_console is not None:
        f_console = open(p.out_console,"w")
    
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
    write_to_console(F"[*] Provider to use: ", end="")
    providerselect = [False,False,False,False] # http, ws, ipc, auto
    if len(p.provider)>0: 
        if p.provider[:4].lower() == "http":
            write_to_console(F"{p.provider} (treated as 'http' provider)")
            providerselect[0] = True
        elif p.provider[:2].lower() == "ws":
            write_to_console(F"{p.provider} (treated as 'ws' provider)")
            providerselect[1] = True
        else:
            write_to_console(F"{p.provider} (treated as 'ipc' provider)")
            providerselect[2] = True
    else:
        write_to_console("not specified, trying web3's auto connect")   
        providerselect[3] = True
        
    
    write_to_console("[*] Connecting...", end="")    
    if providerselect[0]: # http
        w3 = Web3(Web3.HTTPProvider(p.provider))        
    if providerselect[1]: # websocket
        w3 = Web3(Web3.WebsocketProvider(p.provider))   
    if providerselect[2]: # ipc
        w3 = Web3(Web3.IPCProvider(p.provider))         
    if providerselect[3]: # auto
        w3 = Web3()                                     
    
    
    if w3.isConnected():
        write_to_console(" success, we are now connected!",end="\n\n")
    else:
        write_to_console(" could not connect. Exiting...")
        if f_console is not None:
            f_console.close()    
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
    
    write_to_console(F"Latest block: {latestblock.number}")
    write_to_console(F"Block range: {blockmin} - {blockmax} ({blockmax-blockmin+1} {'blocks' if blockmax-blockmin>0 else 'block'})")
    write_to_console(F"Min ether: {w3.fromWei(ethmin_wei,'ether') } ({ethmin_wei} wei)")
    write_to_console(F"Max ether: {w3.fromWei(ethmax_wei,'ether') if ethmax_wei is not None else 'no upper limit'} ({ethmax_wei if ethmax_wei is not None else 'infinite'} wei)")
    if p.skip_zero:
        write_to_console("Not showing transactions with 0 ETH value") 
    
    # open output files
    if p.out_csv is not None:
        f_csv = open(p.out_csv,"w")
        print(csv_delimiter.join(csv_columns),file=f_csv,flush=True)
    
    if p.out_html is not None:
        f_html = open(p.out_html,"w")
        
    
    start = datetime.now()
    
    if f_html is not None:
        print(addHtmlStart((latestblock.number,blockmin,blockmax,ethmin_wei,ethmax_wei,start)),file=f_html,flush=True)
    
    write_to_console("")
    write_to_console("[*] Start @" + str(start),end="\n\n")
    
    
    sumofeth = 0
    numoftx = 0
    for blocknum in range(blockmin,blockmax+1):
        block = w3.eth.getBlock(blocknum)
        write_to_console(F"### Block no. {block.number} ###")
        write_to_console(F"[*] No. of txs in block: {len(block.transactions)}")
        if p.out_blocklink:
            write_to_console(F"[*] {getBlockLink(block.number)}", end="\n\n")
        sumofethinblock = 0
        numoftxinblock = 0
        for tx in block.transactions:
            t = w3.eth.getTransaction(tx)
            if (t.value >= ethmin_wei and ethmax_wei is None) or \
               (t.value >= ethmin_wei and t.value <= ethmax_wei):
                   
                   if t.value==0 and p.skip_zero and p.zero_only is False:
                       continue
                   
                   txstr = str(t.hash.hex()) # tx hash as string
                   
                   write_to_console(F"{txstr}: {w3.fromWei(t.value,'ether')} ETH ({t.value} wei)")
                   
                   if p.out_txlink:
                       write_to_console(F"{getTxLink(txstr)}", end="\n\n")  
                   
                   sumofeth += t.value
                   numoftx += 1
                   sumofethinblock += t.value
                   numoftxinblock += 1
                   
                   data = (numoftx,numoftxinblock,t.value,txstr,block.number)   # (n,nb,value_wei,tx_id,block_number)
                                        
                   if f_csv is not None:
                       print(getCSVLine(data),file=f_csv)
                       
                   if f_html is not None:
                       print(addHtmlLine(data),file=f_html)
                   
        if f_csv is not None:
            f_csv.flush()
        if f_html is not None:
            f_html.flush()
            
        write_to_console("")
        write_to_console(F"Number of filtered txs in this block: {numoftxinblock}")
        write_to_console(F"Sum transfered in these txs in this block: {w3.fromWei(sumofethinblock,'ether')} ETH ({sumofethinblock} wei)")
        write_to_console("")
        
    write_to_console("")
    write_to_console("------------------------------------------")
    write_to_console(F"Total number of filtered txs: {numoftx}")
    write_to_console(F"Total sum transfered in these txs: {w3.fromWei(sumofeth,'ether')} ETH ({sumofeth} wei)")
            
    end = datetime.now()
    write_to_console("")
    write_to_console("[*] End @"+str(end))
    write_to_console("[*] Elapsed time: " + str(end-start))
    
    if f_console is not None:
        f_console.close()    
    
    if f_csv is not None:
        f_csv.close()
    
    if f_html is not None:
        results = (numoftx, sumofeth, str(end),str(end-start))
        print(addHtmlEnd(results),file=f_html)
        f_html.close()

    

