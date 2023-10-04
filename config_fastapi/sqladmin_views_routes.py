from sqladmin import Admin

from src.chat.models import MessageAdmin
from src.delivery.models import OrderAdmin
from src.ibay.models import ProductAdmin
from src.users.models import UserAdmin
from src.wallet.models import AssetAdmin, WalletAdmin, TransactionAdmin


async def init_sqladmin_routes(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(AssetAdmin)
    admin.add_view(WalletAdmin)
    admin.add_view(TransactionAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(MessageAdmin)
