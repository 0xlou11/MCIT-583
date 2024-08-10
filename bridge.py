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
private_key = "0x69aa6fb17552d6092488dd77168d6743822c16c3b7998bc79431ffbe04d633e7" 
admin_address = "0x718301388099942d0af618F2D206cb55EE0ec8bC"  

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
    
    
    if chain == 'source':

        w3 = connectTo('avax')
    
        contract_data = getContractInfo(chain)
        contract_address = contract_data['address']
        contract_abi = contract_data['abi']
        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        latest_block = w3.eth.block_number
        start_block = max(0, latest_block - 4)

        
        event_filter = contract.events.Deposit.create_filter(fromBlock=start_block, toBlock=latest_block)
        events = event_filter.get_all_entries()
        
        for event in events:
            dest_w3 = connectTo('destination')
            dest_contract_data = getContractInfo('destination')
            dest_contract = dest_w3.eth.contract(address=dest_contract_data['address'], abi=dest_contract_data['abi'])
            
            nonce = dest_w3.eth.get_transaction_count(admin_address)
            tx = dest_contract.functions.wrap(
                event['args']['recipient'],
                event['args']['amount']
            ).build_transaction({
                'chainId': dest_w3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': dest_w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = dest_w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = dest_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Wrap transaction sent: {tx_hash.hex()}")
            
    elif chain == 'destination':

        w3 = connectTo('bsc')
    
        contract_data = getContractInfo(chain)
        contract_address = contract_data['address']
        contract_abi = contract_data['abi']
        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        latest_block = w3.eth.block_number
        start_block = max(0, latest_block - 4)
    
        event_filter = contract.events.Unwrap.create_filter(fromBlock=start_block, toBlock=latest_block)
        events = event_filter.get_all_entries()
        
        for event in events:
            source_w3 = connectTo('source')
            source_contract_data = getContractInfo('source')
            source_contract = source_w3.eth.contract(address=source_contract_data['address'], abi=source_contract_data['abi'])
            
            nonce = source_w3.eth.get_transaction_count(admin_address)
            tx = source_contract.functions.deposit(
                event['args']['underlying_token'],
                event['args']['to'],
                event['args']['amount']
            ).build_transaction({
                'chainId': source_w3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': source_w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = source_w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = source_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Deposit transaction sent: {tx_hash.hex()}")
