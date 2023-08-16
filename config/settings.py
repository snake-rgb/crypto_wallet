import os
from pathlib import Path
import environ
from fastapi_mail import ConnectionConfig

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# read env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env('SECRET_KEY')
# database info
DATABASE = {
    'name': env('SQL_DB_NAME'),
    'user': env('SQL_DB_USER'),
    'password': env('SQL_DB_PASSWORD'),
    'host': env('SQL_HOST'),
    'port': env('SQL_PORT'),
}

DB_URL = (f"postgresql+asyncpg://{DATABASE['user']}:"
          f"{DATABASE['password']}"
          f"@{DATABASE['host']}"
          f":{DATABASE['port']}"
          f"/{DATABASE['name']}")

EMAIL_CONF = ConnectionConfig(
    MAIL_USERNAME=env('EMAIL_USER'),
    MAIL_PASSWORD=env('EMAIL_PASSWORD'),
    MAIL_PORT=env('EMAIL_PORT'),
    MAIL_SERVER=env('EMAIL_HOST'),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    MAIL_FROM=env('EMAIL_USER'),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=BASE_DIR / 'src/users/templates',
)
RABBITMQ_URL = env('RABBITMQ_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
ETHEREUM_NODE_URL = env('ETHEREUM_NODE_URL')
MORALIS_API_KEY = env('MORALIS_API_KEY')

# ORIGINS
SOCKET_IO_ORIGINS = [env('SOCKET_IO_ORIGINS')]

HTTP_PROVIDER_URL = env('HTTP_PROVIDER_URL')
WSS_PROVIDER_URL = env('WSS_PROVIDER_URL')

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
