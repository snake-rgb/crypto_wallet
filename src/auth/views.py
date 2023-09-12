from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config_fastapi.config_fastapi import templates

auth_view_router = APIRouter()


@auth_view_router.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", context={'request': request})


@auth_view_router.get("/register/", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", context={'request': request})
