from typing import Callable, Iterator
from sqlalchemy import select
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
                                 value: str,
                                 ) -> Transaction:
        async with self.session_factory() as session:
            transaction = Transaction(
                hash=transaction_hash,
                from_address=from_address,
                to_address=to_address,
                value=value,
            )
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            return transaction

    async def set_balance(self, balance: float, address: str) -> Wallet:
        """
        Method for set wallet balance after import or any other operations
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

    async def create_asset(self, asset_schema: AssetSchema) -> Asset:
        async with self.session_factory() as session:
            asset = Asset(
                image=asset_schema.image,
                short_name=asset_schema.short_name,
                decimal_places=asset_schema.decimal_places,
                symbol=asset_schema.symbol,
            )
            session.add(asset)
            await session.commit()
            await session.refresh(asset)
            return asset

    async def get_wallets_address_in_block(self, wallet_address: list) -> Iterator[str]:
        async with self.session_factory() as session:
            result = await session.execute(select(Wallet).where(Wallet.address.in_(wallet_address)))
            wallets = result.scalars().all()
            wallets_address = [wallet.address for wallet in wallets]
            return wallets_address
