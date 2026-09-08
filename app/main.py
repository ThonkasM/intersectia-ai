import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api import chat, decision
from app.core.config import get_settings
from app.policy import infer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    path = Path(get_settings().trained_policy_path)
    logger.info("trained policy present=%s path=%s active=%s", path.exists(), path, type(infer._policy).__name__)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="IntersectIA AI", lifespan=lifespan)
    app.include_router(decision.router)
    app.include_router(chat.router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()