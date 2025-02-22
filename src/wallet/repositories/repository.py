import datetime
from decimal import Decimal, getcontext
from typing import Callable, Iterator, Optional
from sqlalchemy import select, desc, asc, distinct, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.users.models import User
from src.wallet.enums import TransactionStatus
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
            wallet = result.scalar_one_or_none()
            return wallet

    async def create_transaction(self, transaction_hash: str,
                                 from_address: str,
                                 to_address: str,
                                 value: float,
                                 fee: Optional[float] = None,
                                 age: Optional[datetime.datetime] = None,
                                 status: Optional[TransactionStatus] = None,
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
                asset_id=1
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

    async def create_transaction_bulk(self, transactions: list[dict], moralis_api: bool = None) -> list[Transaction]:
        async with (self.session_factory() as session):
            db_transactions = []
            for transaction in transactions:
                result = await session.execute(
                    select(Transaction).where(Transaction.hash == transaction.get('hash')))
                transaction_db: Transaction = result.scalar_one_or_none()

                # Convert date from string
                date_string = transaction.get('block_timestamp').replace(
                    '.000Z', ''
                ) if moralis_api else transaction.get('age')

                date_format = '%Y-%m-%dT%H:%M:%S'
                age = datetime.datetime.strptime(date_string, date_format)

                if moralis_api:
                    status = TransactionStatus.SUCCESS if transaction.get(
                        'receipt_status') else TransactionStatus.FAILED
                    fee = (float(transaction.get('gas')) * float(transaction.get('gas_price'))) / (
                            10 ** 18)
                    value = float(transaction.get('value')) / (10 ** 18)
                else:
                    status = transaction.get('status')
                    fee = transaction.get('fee')
                    value = transaction.get('value')

                if transaction_db:
                    transaction_db.age = age
                    transaction_db.fee = fee
                    transaction_db.status = status
                    db_transactions.append(transaction_db)
                else:

                    transaction = Transaction(
                        hash=transaction.get('hash'),
                        from_address=transaction.get('from_address'),
                        to_address=transaction.get('to_address'),
                        value=value,
                        age=age,
                        fee=fee,
                        status=status
                    )
                    db_transactions.append(transaction)
                    session.add(transaction)
                await session.commit()
            return db_transactions

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        async with self.session_factory() as session:
            query = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
            transaction = query.scalar_one()
            return transaction

    async def get_user_wallets(self, user_id: int) -> list[Wallet]:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Wallet).options(joinedload(Wallet.asset)).order_by(Wallet.id).where(Wallet.user_id == user_id))
            wallets = query.scalars().all()
            return wallets

    async def get_wallet_by_address(self, wallet_address: str) -> Wallet:
        print(wallet_address)
        async with self.session_factory() as session:
            query = await session.execute(
                select(Wallet).options(joinedload(Wallet.user)).where(Wallet.address == wallet_address))
            wallet = query.scalar_one_or_none()
            return wallet

    async def get_latest_transaction_by_wallet(self, wallet_address: str) -> Transaction:
        async with self.session_factory() as session:
            query = await session.execute(select(Transaction).where(
                Transaction.from_address == wallet_address.lower() or Transaction.to_address == wallet_address.lower()
                and Transaction.status == TransactionStatus.SUCCESS).order_by(
                desc('age')))
            result = query.scalars().first()
            return result

    async def get_wallet_transactions_from_db(self, wallet_address: str) -> list[Transaction]:
        async with self.session_factory() as session:
            query = await session.execute(select(Transaction).where(or_(
                Transaction.from_address == wallet_address.lower(),
                Transaction.to_address == wallet_address.lower()
            )).order_by(desc('age')))
            result = query.scalars().all()
            return result

    async def create_asset(self, asset_schema: AssetSchema):
        async with self.session_factory() as session:
            asset = Asset(**asset_schema.dict())
            session.add(asset)
            await session.commit()
            await session.refresh(asset)
