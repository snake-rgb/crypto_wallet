from propan.brokers.rabbit import RabbitExchange
from web3.datastructures import AttributeDict
from web3.exceptions import InvalidAddress

from config_fastapi.config_fastapi import rabbit_router
from src.web3.web3_api import Web3API
from src.core.register import RegisterContainer

web3_exchange = RabbitExchange(name='web3_exchange')


@rabbit_router.handle('get_balance', exchange=web3_exchange)
async def get_balance(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    try:
        return await web3_api.get_balance(data.get('address'))
    except InvalidAddress:
        return await web3_api.get_balance(await web3_api.to_checksum_address(data.get('address')))


@rabbit_router.handle('get_transaction_count', exchange=web3_exchange)
async def get_transaction_count(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    return await web3_api.web3.eth.get_transaction_count(data.get('from_address'))


@rabbit_router.handle('chain_id', exchange=web3_exchange)
async def chain_id(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    return await web3_api.web3.eth.chain_id


@rabbit_router.handle('convert_ether_to_wei', exchange=web3_exchange)
async def convert_ether_to_wei(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    return await web3_api.convert_ether_to_wei(data.get('amount'))


@rabbit_router.handle('gas_price', exchange=web3_exchange)
async def gas_price(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    return web3_api.web3.to_wei(data.get('price'), data.get('units'))


@rabbit_router.handle('sign_transaction', exchange=web3_exchange)
async def sign_transaction(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    return await web3_api.sign_transaction(data)


@rabbit_router.handle('send_raw_transaction', exchange=web3_exchange)
async def send_raw_transaction(
        data: dict,
) -> str:
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    transaction_hash = await web3_api.send_raw_transaction(data)
    return str(transaction_hash.hex())


@rabbit_router.handle('get_transaction_by_hash', exchange=web3_exchange)
async def get_transaction_by_hash(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    transaction: AttributeDict = await web3_api.web3.eth.get_transaction(data.get('transaction_hash'))
    if transaction.get('blockHash'):
        return {
            'blockHash': transaction.get('blockHash').hex(),
            'blockNumber': transaction.get('blockNumber'),
            'from': transaction.get('from'),
            'gas': transaction.get('gas'),
            'gasPrice': transaction.get('gasPrice'),
            'hash': transaction.get('hash').hex(),
            'input': transaction.get('input').hex(),
            'nonce': transaction.get('nonce'),
            'to': transaction.get('to'),
            'transactionIndex': transaction.get('transactionIndex'),
            'value': transaction.get('value'),
            'type': transaction.get('type'),
            'v': transaction.get('v'),
            'r': transaction.get('r').hex(),
            's': transaction.get('s').hex(),
            'chain_Id': transaction.get('chainId'),
        }
    else:
        return {
            'blockHash': None,
            'blockNumber': None,
            'from': transaction.get('from'),
            'gas': transaction.get('gas'),
            'gasPrice': transaction.get('gasPrice'),
            'hash': transaction.get('hash').hex(),
            'input': transaction.get('input').hex(),
            'nonce': transaction.get('nonce'),
            'to': transaction.get('to'),
            'transactionIndex': transaction.get('transactionIndex'),
            'value': transaction.get('value'),
            'type': transaction.get('type'),
            'v': transaction.get('v'),
            'r': transaction.get('r').hex(),
            's': transaction.get('s').hex(),
            'chain_Id': transaction.get('chainId'),
        }


@rabbit_router.handle('get_transaction_receipt', exchange=web3_exchange)
async def get_transaction_receipt(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    transaction_data: AttributeDict = await web3_api.web3.eth.get_transaction_receipt(data.get('transaction_hash'))
    transaction_receipt: dict = transaction_data.__dict__
    transaction_receipt['blockHash'] = transaction_receipt['blockHash'].hex()
    transaction_receipt['transactionHash'] = transaction_receipt['transactionHash'].hex()
    transaction_receipt['logsBloom'] = transaction_receipt['logsBloom'].hex()
    return transaction_receipt


@rabbit_router.handle('get_block_by_number', exchange=web3_exchange)
async def get_block_by_number(
        data: dict,
):
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    block_data = await web3_api.get_block_by_number(data.get('block_number'))
    block: dict = block_data.__dict__
    return {
        'timestamp': block['timestamp'],
        'transactions': [{
            'blockHash': transaction.get('blockHash').hex(),
            'blockNumber': transaction.get('blockNumber'),
            'hash': transaction.hash.hex(),
            'from': transaction.get('from'),
            'to': transaction.get('to'),
            'gas': transaction.get('gas'),
            'gasPrice': transaction.get('gasPrice'),
            'value': transaction.get('value'),
            'chainId': transaction.get('chainId'),
        } for transaction in block['transactions']]
    }


@rabbit_router.handle('address_is_valid', exchange=web3_exchange)
async def address_is_valid(
        data: dict,
) -> bool:
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    is_valid = web3_api.web3.is_address(data.get('address'))
    return is_valid


@rabbit_router.handle('to_checksum_address', exchange=web3_exchange)
async def to_checksum_address(
        data: dict,
) -> str:
    web3_api: Web3API = RegisterContainer.web3_container.web3_api()
    wallet_address: str = await web3_api.to_checksum_address(data.get('wallet_address'))
    return wallet_address
