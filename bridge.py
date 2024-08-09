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
    config_file_path = Path(__file__).with_name("config.json")
    try:
        with config_file_path.open('r') as f:
            config = json.load(f)
    except Exception as e:
        print("Failed to read config file")
        print(e)
        sys.exit(1)

    private_key = 0x69aa6fb17552d6092488dd77168d6743822c16c3b7998bc79431ffbe04d633e7

    # Connect to the source and destination chains
    source_w3 = connectTo(source_chain)
    destination_w3 = connectTo(destination_chain)

    # Get contract information
    source_contract_info = getContractInfo(source_chain)
    destination_contract_info = getContractInfo(destination_chain)

    source_contract_address = source_contract_info["address"]
    source_contract_abi = source_contract_info["abi"]
    destination_contract_address = destination_contract_info["address"]
    destination_contract_abi = destination_contract_info["abi"]

    # Create contract instances
    source_contract = source_w3.eth.contract(address=source_contract_address, abi=source_contract_abi)
    destination_contract = destination_w3.eth.contract(address=destination_contract_address, abi=destination_contract_abi)

    # Define the event signatures
    deposit_event_signature = source_contract.events.Deposit().signature
    unwrap_event_signature = destination_contract.events.Unwrap().signature

    # Scan the last 5 blocks for the specified chain
    if chain == 'source':
        w3 = source_w3
        contract = source_contract
        event_signature = deposit_event_signature
        other_contract = destination_contract
    else:
        w3 = destination_w3
        contract = destination_contract
        event_signature = unwrap_event_signature
        other_contract = source_contract

    latest_block = w3.eth.blockNumber
    blocks_to_scan = range(latest_block - 4, latest_block + 1)

    account = w3.eth.account.privateKeyToAccount(private_key)

    for block_number in blocks_to_scan:
        block = w3.eth.getBlock(block_number, full_transactions=True)
        for tx in block.transactions:
            receipt = w3.eth.getTransactionReceipt(tx.hash)
            for log in receipt.logs:
                if log.topics[0].hex() == event_signature:
                    event = contract.events.Deposit().processReceipt(receipt) if chain == 'source' else contract.events.Unwrap().processReceipt(receipt)
                    if event:
                        if chain == 'source':
                            # Call the wrap function on the destination chain
                            print(f"Found Deposit event in block {block_number}. Calling wrap function on destination chain.")
                            txn = other_contract.functions.wrap(event['args']['amount']).buildTransaction({
                                'chainId': destination_w3.eth.chain_id,
                                'gas': 2000000,
                                'gasPrice': destination_w3.eth.gas_price,
                                'nonce': destination_w3.eth.getTransactionCount(account.address),
                            })
                            signed_txn = account.sign_transaction(txn)
                            destination_w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                        else:
                            # Call the withdraw function on the source chain
                            print(f"Found Unwrap event in block {block_number}. Calling withdraw function on source chain.")
                            txn = other_contract.functions.withdraw(event['args']['amount']).buildTransaction({
                                'chainId': source_w3.eth.chain_id,
                                'gas': 2000000,
                                'gasPrice': source_w3.eth.gas_price,
                                'nonce': source_w3.eth.getTransactionCount(account.address),
                            })
                            signed_txn = account.sign_transaction(txn)
                            source_w3.eth.sendRawTransaction(signed_txn.rawTransaction)
