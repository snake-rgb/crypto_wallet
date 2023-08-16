from typing import Callable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.models import User


class Boto3Repository:
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory

    async def test(self):
        async with self.session_factory() as session:
            result = await session.execute(select(User))
            # users = result.scalars().all()
            # return users
