Get ethereum transactions by sent ether value. You can set any range of ETH value and filter for transactions in the specified block range.

# Requirements
- Python 3.6+
- [web3py](https://web3py.readthedocs.io/en/stable/quickstart.html#installation)

# Usage

To list all options, use the `-h` flag

> ./gettxbyeth.py -h

## Setting a provider

If you are new to the technical side of Ethereum, I suggest you to register a free account on [infura.io](https://infura.io), create a new project and use one of the endpoint urls you are given. Setting the provider is easy now on:

> ./gettxbyeth.py -p "https://mainnet.infura.io/v3/<your_id>"

You can use any type of provider (http, ws, ipc), the script guesses the type. Only one provider is accepted. If the `-p` flag is omitted, the script falls back to [web3's auto detection](https://web3py.readthedocs.io/en/stable/providers.html#automatic-vs-manual-providers).

## Block settings

`-b`: Sets the exact block to run over on. One block number is accepted.
> ./gettxbyeth.py -p "provider" -b 1234567

`-l`: Select the latest block. You can specify how many blocks to look back.

_Latest block:_
> ./gettxbyeth.py -p "provider" -l      

_Last 5 blocks:_
> ./gettxbyeth.py -p "provider" -l 5     

`-v`, `-n`: Sets the lower and higher end of the block range (inclusive), block number is expected. The default is the latest block in both cases.

_Block range: 11111-22222_
> ./gettxbyeth.py -p "provider" -v 11111 -n 22222     

_Block range: 5555555-latest block_
> ./gettxbyeth.py -p "provider" -v 5555555            

## Ether settings

`-s`: Ignore transactions with 0 ETH value. Other ether options still apply.

`-0`: List transactions with 0 ETH only. Other ether options are ignored.

`-E`: Set the exact ETH value to filter for.

_Search for transactions with exactly 5 ETH only:_
> ./gettxbyeth.py -p "provider" -E 5    

`-w`, `-r`: Set the minimum and maximum ETH to filter for (inclusive). The default value for the minimum is 0, for the maximum is 'no upper limit'.

_List transactions between 5 and 10 ETH:_
> ./gettxbyeth.py -p "provider" -w 5 -r 10    

_List transactions that transfer 5 ETH or above:_
> ./gettxbyeth.py -p "provider" -w 5           

## Output settings

`-oT`, `-oB`: Prints the etherscan.io link to the transaction and to the block.

`-oF`, `-oH`, `-oC`, `-oA`: Saves results to file. Respectively: console output, HTML, CVS, all of the above.

_Copies the console output to file:_
> ./gettxbyeth.py -p "provider" -oF console.txt       

_Generates an HTML output:_
> ./gettxbyeth.py -p "provider" -oH output.html      

_Generates a CSV output. The field delimiter is ';':_
> ./gettxbyeth.py -p "provider" -oC output.csv        

_Generates three files: output.txt, output.html, output.csv:_
> ./gettxbyeth.py -p "provider" -oA output            

The CSV output contains the transaction values in ETH and wei, the transaction hash, the block number that contains the transaction, and links to etherscan.io for both.

## Further examples

When the script is run without parameters, web3py's auto detection kicks in. If successful, the script will list all transactions from the latest block.
> ./gettxbyeth.py


Setting a provider. Same as above, but with a provider specified.
> ./gettxbyeth.py -p "provider"


List all transactions in the last 5 blocks, listing only the ones with a non-zero value.
> ./gettxbyeth.py -p "provider" -s -l 5

List transactions with exatly 10 ether in block 9911399.
> ./gettxbyeth.py -p "provider" -E 10 -b 9911399

List transactions between 5 and 10 ETH in the last 5 blocks and print the output to the fivetoten.html file.
> ./gettxbyeth.py -p "provider" -w 5 -r 10 -l 5 -oH fivetoten.html
