from fastapi import APIRouter
from starlette.responses import HTMLResponse
from fastapi import Request

from config_fastapi.config_fastapi import templates

chat_view_router = APIRouter()


@chat_view_router.get("/chat/", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("chat.html", context={'request': request})
