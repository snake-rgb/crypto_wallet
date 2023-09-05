from dependency_injector import containers, providers

from src.chat.repository.chat import ChatRepository
from src.chat.service.chat import ChatService


class ChatContainer(containers.DeclarativeContainer):
    session = providers.Dependency()
    chat_repository = providers.Singleton(ChatRepository, session)
    chat_service = providers.Singleton(ChatService, chat_repository)
