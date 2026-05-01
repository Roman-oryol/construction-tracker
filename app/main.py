from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.routers import (
    materials,
    projects,
    auth,
    project_members,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Construction Material Tracker", lifespan=lifespan)

app.include_router(materials.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(project_members.router)


@app.get("/")
async def root():
    return {"message": "Construction Tracker is running"}
