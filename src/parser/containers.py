import aioredis
from dependency_injector import containers, providers

from config import settings
from src.parser.services.parser import ParserService


class ParserContainer(containers.DeclarativeContainer):
    web3_api = providers.Dependency()
    wallet_service = providers.Dependency()
    redis = providers.Singleton(aioredis.from_url, settings.REDIS_URL)
    parser_service = providers.Singleton(ParserService, web3_api, redis, wallet_service)
