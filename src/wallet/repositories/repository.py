from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from eth_account import Account
from src.wallet.models import Wallet, Transaction


class WalletRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create_wallet(self, address: str, private_key: str, user_id: int) -> Wallet:
        async with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
                user_id=user_id,
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
                                 value: str,
                                 ) -> Transaction:
        async with self.session_factory() as session:
            transaction = Transaction(
                hash=transaction_hash,
                from_address=from_address,
                to_address=to_address,
                value=value,
            )
            # session.add(transaction)
            # await session.commit()
            # await session.refresh(transaction)
            return transaction

    async def set_balance(self, balance: float, address: str) -> Wallet:
        """
        Method for set wallet balance after import or any other operations
        :param balance: balance in ether
        :param address: wallet address
        :return: wallet instance
        """
        async with self.session_factory() as session:
            result = await session.execute(select(Wallet).where(Wallet.address == address))
            wallet = result.scalar_one()
            wallet.balance = balance
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet

    async def import_wallet(self, private_key: str, address: str, user_id: int) -> Wallet:
        async with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
                user_id=user_id,
            )
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet
