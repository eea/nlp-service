import copy
import importlib
import logging
import os
import os.path

import yaml

import fastapi_chameleon
import uvicorn
import venusian
from app.api.system import router as sys_router
from app.core import config
from app.core.errors.http_error import http_error_handler
from app.core.event_handlers import start_app_handler, stop_app_handler
from app.core.pipeline import (COMPONENTS, add_components_config, add_pipeline,
                               load_components)
from app.views import router as views_router
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

dev_mode = True

folder = os.path.dirname(__file__)
template_folder = os.path.join(folder, "templates")
template_folder = os.path.abspath(template_folder)

fastapi_chameleon.global_init(template_folder, auto_reload=dev_mode)

logger.add("var/nlpservice.log", rotation="500 MB")


def get_app() -> FastAPI:
    """FastAPI app controller"""

    with open(config.CONFIG_YAML_PATH, "r", encoding="utf-8") as stream:
        conf = yaml.safe_load(stream)
        service_names = conf.get("services", [])

    if os.environ.get("NLP_SERVICES"):
        service_names = os.environ["NLP_SERVICES"].strip().split(",")

    loglevel = conf.get("loglevel", int(os.environ.get("NLP_LOGLEVEL", logging.INFO)))

    if loglevel != -1:
        file_handler = logging.FileHandler(
            conf.get("logfile", os.environ.get("NLP_LOGFILE", "/tmp/nlpservice.log"))
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )

        root = logging.getLogger()
        root.setLevel(loglevel)
        root.addHandler(file_handler)

    fast_app = FastAPI(
        title=config.APP_NAME, version=config.APP_VERSION, debug=config.IS_DEBUG
    )

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
    api_router = APIRouter()

    service_descriptions = []

    # instances of each component, loaded based on definitions from the YAML.
    components = {}

    for name in service_names or []:
        logger.info(f"Loading service <{name}> started")
        print(f"Loading service <{name}> started")

        with open(
            os.path.join(config.CONFIG_PATH, f"{name}.yml"), "r", encoding="utf-8"
        ) as stream:
            service_conf = yaml.safe_load(stream)

        service_conf = config.overwrite_with_env_variables(service_conf, name)

        load_components(service_conf, components)

        component_defs = service_conf.get("components", [])
        add_components_config(component_defs)

        pipelines = service_conf.get("pipelines", [])

        for pipeline_def in pipelines:
            pipeline_name = pipeline_def["name"]
            add_pipeline(pipeline_name, [pipeline_def, service_conf])

        pkg = service_conf.get("package", f"app.api.services.{name}")
        tags = service_conf.get("tags", [name])
        prefix = service_conf.get("prefix", f"/{name}")
        service_descriptions.append({"name": name, "conf": service_conf})

        module = importlib.import_module(pkg)
        scanner = venusian.Scanner()
        scanner.scan(module)

        api_router.include_router(module.routes.router, tags=tags, prefix=prefix)
        api_router.include_router(sys_router.router, prefix="/sys")

        logger.info(f"Loading service <{name}> completed")

    COMPONENTS.update(components)

    fast_app.include_router(views_router, prefix="")
    fast_app.include_router(api_router, prefix=config.API_PREFIX)

    def startup():
        app.state.services = service_descriptions

    def startup_tests():
        if os.environ.get("DISABLE_RUNTIME_TESTS"):
            return

        for service in app.state.services or []:
            name = service.get("name")
            logger.info(f"Starting runtime test for <{name}> service")
            pkg = service.get("conf", {}).get("package", f"app.api.{name}")
            module = importlib.import_module(pkg)
            module.runtimetest.runtimetest(app)
            logger.info(f"Runtime test for <{name}> completed")

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("startup", startup)
    fast_app.add_event_handler("startup", startup_tests)
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    static_media_path = os.environ.get("STATIC_MEDIA")
    if static_media_path:
        if not os.path.exists(static_media_path):
            os.mkdir(static_media_path)
        app.mount("/static", StaticFiles(directory=static_media_path), name="static")

    if config.IS_DEBUG:
        logger.info("See http://127.0.0.1:8000/docs for Swagger API Documentation.")

    return fast_app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
