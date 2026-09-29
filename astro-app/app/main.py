import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import auth, chart, payments, readings, telegram
from app.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # for production, switch to Alembic migrations
    sched = start_scheduler()
    yield
    sched.shutdown()


app = FastAPI(title="Stellar Chart API", lifespan=lifespan)
for r in (auth.router, chart.router, payments.router, readings.router, telegram.router):
    app.include_router(r)


@app.get("/api/health")
def health():
    return {"ok": True}


app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend", html=True), name="frontend")
