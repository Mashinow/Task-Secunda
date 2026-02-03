from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.database import Base, async_session_factory, engine
from app.routes import router
from app.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await seed(session)
    logging.getLogger("uvicorn").info('Сервис запущен на http://127.0.0.1:8000')
    yield


app = FastAPI(
    title="Справочник организаций",
    description="REST API справочника Организаций, Зданий, Деятельности",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_headers=["X-API-Key"],
    allow_methods=["GET", "POST"],
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    app.mount("/static", StaticFiles(directory="static"), name="static")
    uvicorn.run(app, host="0.0.0.0", port=8000)
