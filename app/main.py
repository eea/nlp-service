import uvicorn
import venusian
from fastapi import FastAPI, HTTPException
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app import services
from app.api.errors.http_error import http_error_handler
from app.api.routes.router import api_router
from app.core.config import API_PREFIX, APP_NAME, APP_VERSION, IS_DEBUG
from app.core.event_handlers import start_app_handler, stop_app_handler


def get_app() -> FastAPI:
    """FastAPI app controller"""

    scanner = venusian.Scanner()
    scanner.scan(services)

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    # This middleware enables allow all cross-domain requests to the API
    # from a browser.
    # For production deployments, it could be made more restrictive.
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_app.add_exception_handler(HTTPException, http_error_handler)

    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    if IS_DEBUG:
        logger.info("Open http://127.0.0.1:8000/docs to see Swagger API Documentation.")
        logger.info(
            """
        Or just try it out directly:
        curl --request POST --url 'http://127.0.0.1:8000/query' \
                --data '{"query": "Did Albus Dumbledore die?"}'
        """
        )

    return fast_app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
