from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.model import MODELS


def _startup_models(app: FastAPI) -> None:
    for name, Model in MODELS.items():
        logger.info(f"Init model: {name}")
        setattr(app.state, name, Model())


def _shutdown_model(app: FastAPI) -> None:
    for name, Model in MODELS.items():
        logger.info(f"Shutdown model: {name}")
        setattr(app.state, name, None)


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_models(app)

    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)

    return shutdown
