import logging

from fastapi import FastAPI

from app import __version__
from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, version=__version__)
    app.include_router(health.router)
    logger.info("app_started", extra={"environment": settings.environment})
    return app


app = create_app()