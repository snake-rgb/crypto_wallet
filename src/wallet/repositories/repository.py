import datetime
from decimal import Decimal, getcontext
from typing import Callable, Iterator, Optional
from hexbytes import HexBytes
from sqlalchemy import select, bindparam, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.wallet.models import Wallet, Transaction, Asset
from src.wallet.schemas import AssetSchema


class WalletRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create_wallet(
            self,
            address: str,
            private_key: str,
            user_id: int,
            asset_id: int) -> Wallet:
        async with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
                user_id=user_id,
                asset_id=asset_id,
            )
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet

    async def get_wallet(self, address: str) -> Wallet:
        async with self.session_factory() as session:
            result = await session.execute(select(Wallet).where(Wallet.address == address))
            wallet = result.scalar_one()
            return wallet

    async def create_transaction(self, transaction_hash: str,
                                 from_address: str,
                                 to_address: str,
                                 value: float,
                                 fee: Optional[float] = None,
                                 age: Optional[datetime.datetime] = None,
                                 status: Optional[bool] = None,
                                 ) -> Transaction:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Transaction).where(Transaction.hash == transaction_hash))

            existing_transaction: Transaction = query.scalar_one_or_none()
            if existing_transaction:
                existing_transaction.status = 'SUCCESS' if status else 'FAILED'
                existing_transaction.age = age
                existing_transaction.fee = fee
                session.add(existing_transaction)
                await session.commit()
                await session.refresh(existing_transaction)
                return existing_transaction
            else:
                transaction = Transaction(
                    hash=transaction_hash,
                    from_address=from_address,
                    to_address=to_address,
                    value=value,
                    age=age,
                    fee=fee,
                    status='SUCCESS' if status else 'PENDING' if status is None else 'FAILED',
                )

                session.add(transaction)
                await session.commit()
                await session.refresh(transaction)
                return transaction

    async def set_balance(self, balance: float, address: str) -> Wallet:
        """
        Method for set wallet balance after import
        :param balance: balance in ether
        :param address: wallet address
        :return: wallet instance
        """
        async with self.session_factory() as session:
            # get wallet
            result = await session.execute(select(Wallet).where(Wallet.address == address))
            wallet = result.scalar_one()

            # get asset
            result = await session.execute(select(Asset).where(Asset.id == wallet.asset_id))
            asset = result.scalar_one()

            wallet.balance = balance / (10 ** asset.decimal_places)
            session.add(wallet)

            await session.commit()
            await session.refresh(wallet)
            return wallet

    async def change_balance(self, value: float, address: str, operation_type: str) -> Wallet:
        async with self.session_factory() as session:
            getcontext().prec = 18
            # get wallet
            result = await session.execute(select(Wallet).where(Wallet.address == address))
            wallet: Wallet = result.scalar_one_or_none()

            if operation_type == 'add' and wallet:
                wallet.balance += Decimal(value)
            elif operation_type == 'subtract' and wallet:
                wallet.balance -= Decimal(value)
            if wallet:
                session.add(wallet)
                await session.commit()
                await session.refresh(wallet)

    async def import_wallet(self, private_key: str, address: str, user_id: int) -> Wallet:
        async with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
                user_id=user_id,
                # hardcode eth asset
                asset_id=2
            )
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet

    async def get_wallets_address_in_block(self, wallet_address: list) -> Iterator[str]:
        async with self.session_factory() as session:
            result = await session.execute(select(Wallet).where(Wallet.address.in_(wallet_address)))
            wallets = result.scalars().all()
            wallets_address = [wallet.address for wallet in wallets]
            return wallets_address

    # TODO: Сделать апдейт множества транзакций
    async def create_transaction_bulk(self, transactions: list[dict]) -> None:
        async with self.session_factory() as session:
            await session.commit()

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        async with self.session_factory() as session:
            query = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
            transaction = query.scalar_one()
            return transaction
