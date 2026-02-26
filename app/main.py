from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.db import create_db_tables, engine
import logging

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        )

logger = logging.getLogger("quick_notes")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Create tables for sqlite db
    Shutdown: Wait for db engine to shutdown
    """
    logger.info("Starting server.. creating database")
    await create_db_tables()
    logger.info("Database ready")

    yield

    logger.info("Shutting down application.. disposing db")
    await engine.dispose()
    logger.info("Graceful shutdown complete.")

app = FastAPI(
        title  = "Quick Notes API",
        version="1.0",
        lifespan=lifespan,
        )

@app.get("/")
def root():
    return {"message": "hello world"}
