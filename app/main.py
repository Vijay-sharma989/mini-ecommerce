from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db
from app.auth.router import router as auth_router

app = FastAPI(
    title = "Mini E-Commerce API",
    description = "E-Commerce Backend Build with FastAPI",
    version = "1.0.0"
)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Mini E-Commerce API"
    }


@app.get('/db-test')
async def database_test(db:AsyncSession = Depends(get_db)):
    results = await db.execute(text("SELECT 1"))

    return {
        "Database" : "Connected",
        "result": results.scalar()
    }