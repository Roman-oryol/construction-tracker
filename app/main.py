from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.routers import (
    materials,
    projects,
    auth,
    project_members,
    deliveries,
    consumptions,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Construction Material Tracker", lifespan=lifespan)

# CORS — разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(materials.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(project_members.router)
app.include_router(deliveries.router)
app.include_router(consumptions.router)


@app.get("/")
async def root():
    return {"message": "Construction Tracker is running"}
