from typing import Callable
from sqlalchemy.orm import Session
from eth_account import Account
from src.wallet.models import Wallet


class WalletRepository:
    def __init__(self, session_factory: Callable[..., Session]) -> None:
        self.session_factory = session_factory

    async def create_wallet(self, address: str, private_key: str, user_id: int):
        with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
                user_id=user_id,
            )
            session.add(wallet)
            session.commit()
            session.refresh(wallet)
            return wallet

    async def get_wallet(self, address: str) -> Wallet:
        with self.session_factory() as session:
            wallet = session.query(Wallet).filter(Wallet.address == address).first()
            return wallet

    async def send_transaction(self, from_address: str, to_address: str) -> None:
        pass

    async def set_balance(self, balance: float, address: str) -> Wallet:
        """
        Method for set wallet balance after import or any other operations
        :param balance: balance in ether
        :param address: wallet address
        :return: wallet instance
        """
        with self.session_factory() as session:
            wallet = session.query(Wallet).filter(Wallet.address == address).first()
            wallet.balance = balance
            session.add(wallet)
            session.commit()
            session.refresh(wallet)
            return wallet

    async def import_wallet(self, private_key: str, address: str) -> Wallet:
        with self.session_factory() as session:
            wallet = Wallet(
                address=address,
                balance=0,
                private_key=private_key,
            )
            session.add(wallet)
            session.commit()
            session.refresh(wallet)
            return wallet
