from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.base import Base
from app.database import engine
from app.routers import materials
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Construction Material Tracker", lifespan=lifespan)

app.include_router(materials.router)


@app.get("/")
async def root():
    return {"message": "Construction Tracker is running"}
