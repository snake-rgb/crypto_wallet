import asyncio
import os
from dependency_injector.wiring import inject
from starlette.responses import Response
from src.auth.schemas import RegisterSchema
from src.auth.services.auth import AuthService
from src.core.register import RegisterContainer
from src.ibay.schemas import ProductSchema
from src.ibay.services.ibay import IbayService
from src.wallet.schemas import AssetSchema
from src.wallet.service.wallet import WalletService


class InitDatabase:
    def __init__(self, register_container: RegisterContainer):
        self.db = RegisterContainer.core_container.db()
        self.register_container = register_container
        self.migrate()

    @staticmethod
    def migrate():
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
        register_schema_admin = RegisterSchema(
            username='admin',
            email='admin@admin.com',
            password='1230123viK',
            confirm_password='1230123viK',
            profile_image=None
        )
        await self.create_user(register_schema, self.register_container.auth_container.auth_service())
        await self.create_superuser(register_schema_admin, self.register_container.auth_container.auth_service())
        await self.create_asset(self.register_container.wallet_container.wallet_service())
        await self.create_wallet(self.register_container.wallet_container.wallet_service())
        await self.create_product(self.register_container.ibay_container.ibay_service())

    @inject
    async def create_user(self, register_schema: RegisterSchema, auth_service: AuthService):
        hashed_password = auth_service.password_hasher(register_schema.password)
        await auth_service.auth_repository.register(register_schema,hashed_password=hashed_password)

    @inject
    async def create_superuser(self, register_schema: RegisterSchema, auth_service: AuthService):
        await auth_service.register_superuser(register_schema, response=Response())

    @inject
    async def create_wallet(self, wallet_service: WalletService):
        await wallet_service.create_wallet(1, 1)

    @inject
    async def create_asset(self, wallet_service: WalletService):
        asset_schema = AssetSchema(
            image=None,
            decimal_places=18,
            short_name='SETH',
            symbol='SepoliaETH',
        )
        await wallet_service.create_asset(asset_schema)

    @inject
    async def create_product(self, ibay_service: IbayService):
        product_schema = ProductSchema(name='Product 1',
                                       image="""data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAACi1BMVEUAAAAbLBQLEAkCAwL///8QGgwRGw4YKBIRGxAECAQuExNHNhMtEhIvTSMAAAAPFgwdKxgGCAUbKhUIDQYAAAAbJxZWfUY1TitNdTwGDAUAAAAAAAAAAAAUHRAySCl1qmBmlVMnPB8KEQgKEAgiNxsQGwwLEgpNbz85Wi4AAAAVBwhNIyE5XSwAAAAlHg2FbzFwWSIYEQULBQV1MDBShUAZKhMEAwGMczJlTRsAAAAMBQV0Ly80Vyg/NBfBljdRPBZzLi9BbjNsWSfQpUGIRDLdWVpGdzeCay9GdjeAai42XCpFOBlUhkEeMRZRMTE+ZjAAAACMVVVLeTsRHA2KU1NHcDgUIg97Skrrjo6qX16kgTIxPx8tSCUHDAWOVlZyRUWBTk59S0t/TEw5IB9YSB+LcjF2XycsIgwAAAB8tGZukVBwjEtpj01YdT7UrkzkuVDIo0XbWFmGUD/6z1rwxlbft1DswlXPpkPNU1PFUFBcdz7btE//1FzatE6TeTXUr0yUeTTeW1vjXFzQVVXjWlxqYjz5zVnTrkyfgjnKpUibfzflvVLwYmLnXl6wSEjiWVuHa0j3y1jIpEfRrEvzyFfLpUiSTzngWlvvYWHeWlrSVlbpXF6YhVXtxFSMczG9nEPrwlPLp0huQCqiQ0LBUE/lXV7tYWHSVVXNUlNedD6OZkKFV0llQzaaZlFLMyGBYy+9mESjfTiUTzbDT1C4S0vxYWKPTEHag4TykpLdhYb4lJaxY2KzkEL5z1rqwVPMo0CcSjvoXV6xS0pfeEH4lpb3lZXif4GbcD790Vr/0lz4yVKLVS2WRUJjdEP+0Vr0xE9mYCxag0j2lJT1lJT3lJWohT3/01z5y1f////6otc5AAAAaXRSTlMAAAAAAAAAAAAAAAAAAAekljizfQ53+ePxUQkBCoDa/ffUWTSuOz/v1R8yzr0WW/HfPDLO+m464cgXMM7EnvRxyvDa/fD+/e70583D/HzFyyD36Uv23FSj+v752pIrGLDv5uyiu/LccwPjgbrLAAAAAWJLR0QEj2jZUQAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAAd0SU1FB+cHFQ0eENNcRs8AAAEUSURBVBjTY2Dg4xcQFBJmZIABJhFRMXEJSSlmIFtaRpqBgUVWTj5TQVGJlYGBTVlFlZ2BQ009KztHQ5OTgUtLO1dHl4FBTz8vv8DAkJvHyLiwyMSUwcy8uKS0rNzC0sq6orKyyobBtrqmtq6+wc7eobGpuaXVkcGprb2js6vb2cW1p7evf4Ibg/vESZOn5E2dNr1nxsxZs+d4MHjOnTd/wcJFi5csXba8csVKLwbvVavXrF23fsPGTZu3bN3m48vgt33Hzl279+zdt//AwUOH/QMYAo8cPXLk2PETJ0+dPnM2KJiXIeTo0aNAgXMnz1+4GBoG9Et4xKXLVyKvXrseFR0TC/JtXHxCYlJySmpaekAGiA8AzvBkGNwMPxcAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjMtMDctMjFUMTM6MzA6MTYrMDA6MDAT05+yAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIzLTA3LTIxVDEzOjMwOjE2KzAwOjAwYo4nDgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABXelRYdFJhdyBwcm9maWxlIHR5cGUgaXB0YwAAeJzj8gwIcVYoKMpPy8xJ5VIAAyMLLmMLEyMTS5MUAxMgRIA0w2QDI7NUIMvY1MjEzMQcxAfLgEigSi4A6hcRdPJCNZUAAAAASUVORK5CYII=""",
                                       wallet_address='0x9841b300b8853e47b7265dfF47FD831642e649e0',
                                       price=0.0001)
        await ibay_service.create_product(product_schema)


if __name__ == '__main__':
    database = InitDatabase(RegisterContainer())


    async def main():
        await database()


    asyncio.run(main())
