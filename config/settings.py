import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# read env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# database info
DATABASE = {
    'name': env('SQL_DB_NAME'),
    'user': env('SQL_DB_USER'),
    'password': env('SQL_DB_PASSWORD'),
    'host': env('SQL_HOST'),
    'port': env('SQL_PORT'),
}

DB_URL = (f"postgresql://{DATABASE['user']}:"
          f"{DATABASE['password']}"
          f"@{DATABASE['host']}"
          f":{DATABASE['port']}"
          f"/{DATABASE['name']}")
