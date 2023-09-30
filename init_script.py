import asyncio
import os
from typing import Callable

from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.auth.schemas import RegisterSchema
from src.auth.services.auth import AuthService
from src.core.register import RegisterContainer
from src.users.models import User


class InitDatabase:
    def __init__(self, register_container: RegisterContainer):
        self.db = RegisterContainer.core_container.db()
        self.register_container = register_container
        self.migrate()

    def migrate(self):
        os.system('make makemigrations')
        os.system('make migrate')

    async def __call__(self, *args, **kwargs):
        register_schema = RegisterSchema(
            username='user',
            email='user@user.com',
            password='1230123viK',
            confirm_password='1230123viK',
            profile_image=None
        )
        await self.create_user(register_schema, self.register_container.auth_container.auth_service())

    @inject
    async def create_user(self, register_schema: RegisterSchema, auth_service: AuthService):
        await auth_service.register(register_schema, response=Response())


if __name__ == '__main__':
    database = InitDatabase(RegisterContainer())


    async def main():
        await database()


    asyncio.run(main())
