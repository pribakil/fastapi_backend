
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import text
from starlette.responses import JSONResponse
from src.core.database import engine
from src.routers import user_router_v1, user_router_v2, arbo20_router_v1

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # uncomment to drop all tables
        # await conn.run_sync(SQLModel.metadata.create_all) # For first lqunch or testing only; in Production we use the Alembic migrations instead
     
            await conn.execute(text("SELECT 1"))
            print("Database connection succeeded !")
    except Exception as e:
        print("Database connection failled: ", e)
        raise e

    yield

    await engine.dispose()
    
    print("Database engine disposed !")

app = FastAPI(lifespan = lifespan)

app.include_router(user_router_v1)
app.include_router(user_router_v2)
app.include_router(arbo20_router_v1)

@app.exception_handler(HTTPException)
async def handle_http_exception(request:Request, exc:HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.get("/health", tags = ["System"])
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "Ok", "database": "connection succeeded !"}
    except Exception as e:
        print(str(e))
        return {"status": "error", "database": "connextion failed, please contact the admin."}