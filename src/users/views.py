from fastapi import Request, APIRouter
from starlette.responses import HTMLResponse

from config_fastapi.config_fastapi import templates

user_view_router = APIRouter()


@user_view_router.get("/profile/", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", context={'request': request})


@user_view_router.get("/", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", context={'request': request})


@user_view_router.get("/asyncapi/", response_class=HTMLResponse)
async def asyncapi(request: Request):
    return templates.TemplateResponse("/asyncapi_docs/index.html", context={'request': request})
