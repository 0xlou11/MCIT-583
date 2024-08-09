from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
import sys
from pathlib import Path

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['avax','bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def getContractInfo(chain):
    """
        Load the contract_info file into a dictinary
        This function is used by the autograder and will likely be useful to you
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( "Failed to read contract info" )
        print( "Please contact your instructor" )
        print( e )
        sys.exit(1)

    return contracts[chain]




def scanBlocks(chain):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return
    
        #YOUR CODE HERE
    source_w3 = connectTo(source_chain)
    destination_w3 = connectTo(destination_chain)
    source_contract_info = getContractInfo(source_chain)
    destination_contract_info = getContractInfo(destination_chain)

    source_contract = source_w3.eth.contract(address=source_contract_info['address'], abi=source_contract_info['abi'])
    destination_contract = destination_w3.eth.contract(address=destination_contract_info['address'], abi=destination_contract_info['abi'])

    latest_block = source_w3.eth.block_number
    start_block = latest_block - 4
    end_block = latest_block

    headers = ['chain', 'token', 'recipient', 'amount', 'transactionHash', 'address']
    eventfile = 'bridge_events.csv'
    try:
        pd.read_csv(eventfile)
    except FileNotFoundError:
        pd.DataFrame(columns=headers).to_csv(eventfile, index=False)

    for block_num in range(start_block, end_block + 1):
        event_filter = source_contract.events.Deposit.create_filter(fromBlock=block_num, toBlock=block_num)
        events = event_filter.get_all_entries()
        rows = []
        for event in events:
            row = {
                'chain': source_chain,
                'token': event['args']['token'],
                'recipient': event['args']['recipient'],
                'amount': event['args']['amount'],
                'transactionHash': event['transactionHash'].hex(),
                'address': source_contract_info['address']
            }
            rows.append(row)
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(eventfile, mode='a', index=False, header=False)

