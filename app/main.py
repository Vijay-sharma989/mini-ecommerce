from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import get_db
from app.auth.router import router as auth_router
from app.routers.users import router as user_router
from app.routers.categories import router as category_router
from app.routers.product import router as product_router
from app.routers.cart import router as cart_router

app = FastAPI(
    title = "Mini E-Commerce API",
    description = "E-Commerce Backend Build with FastAPI",
    version = "1.0.0"
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)

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