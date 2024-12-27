from fastapi import FastAPI, Request
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pathlib import Path


from app.config.logger import logger
from typing import Callable
from app.routers import contacts, auth, users, configurate
from app.config.configurate import settings, configure_cors, lifespan
from fastapi.templating import Jinja2Templates
from app.middleware.middleware_set import user_agent_ban_middleware
from app.middleware.middleware_set import banned_ips_middleware


BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
configure_cors(app)


@app.middleware("http")
async def add_user_agent_ban_middleware(request: Request, call_next: Callable):
    return await user_agent_ban_middleware(request, call_next)


@app.middleware("http")
async def add_banned_ip_middleware(request: Request, call_next: Callable):
    return await banned_ips_middleware(request, call_next)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "templates" / "static"),
    name="static",
)

app.include_router(router=users.router, prefix="/api")
app.include_router(router=contacts.router, prefix="/api")
app.include_router(router=auth.router, prefix="/api")
app.include_router(router=configurate.router, prefix="/api")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        },
    )
