from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from app.db.get_session import get_connection_db
from app.config.logger import logger
from app.routers import contacts, auth, users
from app.config.configurate import settings, configure_cors, lifespan
from fastapi.templating import Jinja2Templates

app = FastAPI(lifespan=lifespan)
templates =  Jinja2Templates(directory='app/templates')
configure_cors(app)

app.mount('/static', StaticFiles(directory='app/templates/static'),name='static')

app.include_router(
    router=users.router,
    prefix='/api'
)
app.include_router(
    router = contacts.router, 
    prefix = "/api"
    )
app.include_router(
    router=auth.router,
    prefix='/api'
)

@app.get('/')
def index(request:Request):
    return templates.TemplateResponse(
        'home.html',
        {
            'request':request,
            
        }
    )

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_connection_db)):
    """вроверка подклюяения к базе данных"""
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail="Database is not configured correctly"
                )
        return {
            "message": "Data base normaly work"
            }
    except Exception as err:    
        logger.critical(f'Database connection error, {err}')
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to the database"
            )

