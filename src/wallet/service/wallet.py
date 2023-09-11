import datetime
from fastapi import HTTPException
from eth_account import Account
import secrets
from propan import RabbitBroker
from web3.datastructures import AttributeDict
from config import settings
from src.wallet.enums import TransactionStatus
from src.wallet.models import Wallet, Transaction
from src.wallet.repositories.repository import WalletRepository


class WalletService:

    def __init__(self, wallet_repository: WalletRepository,
                 ) -> None:
        self.wallet_repository = wallet_repository

    async def create_wallet(self, user_id: int, asset_id: int) -> Wallet:
        # random string hex
        private = secrets.token_hex(32)
        private_key = "0x" + private
        # create account
        account = Account.from_key(private_key)
        return await self.wallet_repository.create_wallet(address=account.address, private_key=private_key,
                                                          user_id=user_id, asset_id=asset_id)

    @staticmethod
    async def get_balance(address: str) -> float:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            balance: float = await broker.publish({
                'address': address, },
                queue='get_balance',
                exchange='web3_exchange',
                callback=True)
            return balance

    async def send_transaction(self, from_address: str, to_address: str, amount: float) -> Transaction:
        sender_wallet = await self.wallet_repository.get_wallet(from_address)
        # gas_amount
        gas = 21000
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            nonce = await broker.publish({
                'from_address': from_address
            },
                queue='get_transaction_count',
                exchange='web3_exchange',
                callback=True)
            chain_id = await broker.publish({
                'from_address': from_address
            },
                queue='chain_id',
                exchange='web3_exchange',
                callback=True)
            value = await broker.publish({
                'amount': amount
            },
                queue='convert_ether_to_wei',
                exchange='web3_exchange',
                callback=True)
            gas_price = await broker.publish({
                'price': 50,
                'units': 'gwei'
            },
                queue='gas_price',
                exchange='web3_exchange',
                callback=True)
            transaction: dict = await broker.publish({
                'chainId': chain_id,
                'from': from_address,
                'to': to_address,
                'value': value,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': gas,
                'private_key': sender_wallet.private_key
            },
                queue='sign_transaction',
                exchange='web3_exchange',
                callback=True)
            signed_transaction: dict = transaction

            transaction_hash = await broker.publish(
                signed_transaction,
                queue='send_raw_transaction',
                exchange='web3_exchange',
                callback=True)

            db_transaction = await self.wallet_repository.create_transaction(
                transaction_hash=transaction_hash,
                from_address=from_address,
                to_address=to_address,
                value=amount,
            )
            return db_transaction

    @staticmethod
    async def get_wallet_transactions(address: str, limit: int) -> dict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transactions: dict = await broker.publish({
                'address': address,
                'limit': f'{limit}'
            },
                queue='get_native_transactions',
                exchange='moralis_exchange',
                callback=True
            )
            return transactions

    @staticmethod
    async def get_transaction_by_hash(transaction_hash: str) -> dict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transaction: AttributeDict = await broker.publish({
                'transaction_hash': transaction_hash,
            },
                queue='get_transaction_by_hash',
                exchange='web3_exchange',
                callback=True
            )
            return transaction

    async def import_wallet(self, private_key: str, access_token: str) -> Wallet:
        try:
            account = Account.from_key(private_key)
            address = account.address
            balance = await self.get_balance(address)
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                user_id: int = await broker.publish({
                    'access_token': access_token,
                },
                    queue='get_user_id',
                    exchange='user_exchange',
                    callback=True
                )
                if balance and user_id:
                    wallet = await self.wallet_repository.import_wallet(private_key, address, user_id=user_id)
                    await self.wallet_repository.set_balance(balance, wallet.address)
                    return wallet
                else:
                    raise HTTPException(status_code=400, detail='Wallet exception')
        except ValueError:
            raise HTTPException(status_code=400,
                                detail='The private key must be exactly 32 bytes long, instead of 3 bytes.')

    async def get_wallets_address_in_block(self, wallet_address: list) -> list[str]:
        return set(await self.wallet_repository.get_wallets_address_in_block(wallet_address))

    @staticmethod
    async def get_transaction_receipt(transaction_hash: str) -> AttributeDict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transaction_receipt: dict = await broker.publish({
                'transaction_hash': transaction_hash,
            },
                queue='get_transaction_receipt',
                exchange='web3_exchange',
                callback=True
            )
            return transaction_receipt

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        return await self.wallet_repository.get_transaction_by_id(transaction_id)

    async def buy_product(self, data: dict) -> None:
        from_address = data.get('from_address')
        to_address = data.get('to_address')
        amount = data.get('amount')
        transaction = await self.send_transaction(from_address, to_address, amount)
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish({
                'product_id': data.get('product_id'),
                'transaction_id': transaction.id,
                'customer_id': data.get('customer_id'),
            }, queue='create_order', exchange='ibay_exchange')

    async def order_refund(self, data) -> None:
        from_address = data.get('from_address')
        to_address = data.get('to_address')
        amount = data.get('amount')
        transaction = await self.send_transaction(from_address, to_address, amount)
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish({
                'order_id': data.get('order_id'),
                'return_transaction_id': transaction.id,
                'customer_id': data.get('customer_id'),
            }, queue='order_refund', exchange='ibay_exchange')

    async def create_transaction(
            self,
            transaction_hash: str,
            from_address: str,
            to_address: str,
            value: float,
            age: datetime.datetime,
            status: TransactionStatus,
            fee: float,
    ) -> Transaction:
        transaction: Transaction = await self.wallet_repository.create_transaction(
            transaction_hash=transaction_hash,
            from_address=from_address,
            to_address=to_address,
            value=value,
            age=age,
            status=status,
            fee=fee,
        )
        return transaction

    async def change_balance(
            self,
            address: str,
            value: float,
            operation_type: str,
    ) -> Wallet:
        return await self.wallet_repository.change_balance(
            address=address,
            value=value,
            operation_type=operation_type,
        )

    async def get_user_wallets(self, user_id) -> list[Wallet]:
        return await self.wallet_repository.get_user_wallets(user_id)
