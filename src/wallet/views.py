from fastapi import Request, APIRouter
from starlette.responses import HTMLResponse

from config_fastapi.config_fastapi import templates

wallet_view_router = APIRouter()


@wallet_view_router.get("/wallets/", response_class=HTMLResponse)
async def wallets(request: Request):
    return templates.TemplateResponse("wallets.html", context={'request': request})
