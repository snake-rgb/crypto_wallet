import aioredis
from dependency_injector import containers, providers

from config import settings
from src.parser.services.parser import ParserService


class ParserContainer(containers.DeclarativeContainer):
    celery = providers.Dependency()
    redis = providers.Singleton(aioredis.from_url, settings.REDIS_URL)
    parser_service = providers.Singleton(ParserService, celery, redis)
