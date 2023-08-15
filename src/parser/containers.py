from dependency_injector import containers, providers
from src.parser.parser import ParserService


class ParserContainer(containers.DeclarativeContainer):
    web3_api = providers.Dependency()
    parser_service = providers.Singleton(ParserService, web3_api)
