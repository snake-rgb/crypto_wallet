from starlette.templating import Jinja2Templates
from config import settings
from propan import RabbitBroker

broker = RabbitBroker(settings.RABBITMQ_URL, timeout=120)
templates = Jinja2Templates(directory='templates')






