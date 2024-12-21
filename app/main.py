from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.get_session import get_connection_db
from app.config.logger import logger

app = FastAPI()


@app.get('/')
def index():
    return {
        'message':'this is a contacts aplication'
    }

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
    