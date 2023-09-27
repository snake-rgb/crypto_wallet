from fastapi import Request, APIRouter
from starlette.responses import HTMLResponse

from config_fastapi.config_fastapi import templates

ibay_view_router = APIRouter()


@ibay_view_router.get("/ibay/", response_class=HTMLResponse)
async def wallets(request: Request):
    return templates.TemplateResponse("ibay.html", context={'request': request})
