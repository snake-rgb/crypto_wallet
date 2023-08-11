from dependency_injector import containers, providers
from config.settings import DB_URL
from src.core.database import Database


class CoreContainer(containers.DeclarativeContainer):
    db = providers.Singleton(Database, db_url=DB_URL)
    session = providers.Callable(db.provided.session)
