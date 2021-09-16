import copy
import importlib
import os
import os.path

import fastapi_chameleon
import uvicorn
import venusian
import yaml
from fastapi import APIRouter, FastAPI, HTTPException
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.core import config
from app.core.errors.http_error import http_error_handler
from app.core.event_handlers import start_app_handler, stop_app_handler
from app.core.pipeline import add_pipeline
from app.views import router as views_router

dev_mode = True

folder = os.path.dirname(__file__)
template_folder = os.path.join(folder, 'templates')
template_folder = os.path.abspath(template_folder)

fastapi_chameleon.global_init(template_folder, auto_reload=dev_mode)


def load_components(config):
    from haystack.schema import BaseComponent
    components = {}  # definitions of each component from the YAML.

    for definition in config.get("components", []):
        copied = copy.deepcopy(definition)
        name = copied.pop("name")
        params = copied.get('params', {})

        # loads references to other components
        for k, v in params.items():
            if isinstance(v, str) and v in components:
                params[k] = components[v]

        components[name] = BaseComponent.load_from_args(
            copied['type'], **params
        )

    return components


def get_app() -> FastAPI:
    """FastAPI app controller"""

    if os.environ.get('NLP_SERVICES'):
        service_names = os.environ['NLP_SERVICES'].strip().split(',')
    else:
        with open(config.CONFIG_YAML_PATH, "r", encoding='utf-8') as stream:
            conf = yaml.safe_load(stream)
            service_names = conf.get('services', [])

    fast_app = FastAPI(title=config.APP_NAME,
                       version=config.APP_VERSION, debug=config.IS_DEBUG)

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

    for name in (service_names or []):
        logger.info(f"Loading service <{name}> started")
        with open(os.path.join(config.CONFIG_PATH, f"{name}.yml"), "r",
                  encoding='utf-8') as stream:
            service_conf = yaml.safe_load(stream)

        service_conf = config.overwrite_with_env_variables(service_conf, name)

        load_components(service_conf)
        for pipeline_def in service_conf.get('pipelines', []):
            pipeline_name = pipeline_def['name']
            add_pipeline(pipeline_name, [pipeline_def, service_conf])

        pkg = service_conf.get('package', f"app.api.services.{name}")
        tags = service_conf.get('tags', [name])
        prefix = service_conf.get('prefix', f"/{name}")

        module = importlib.import_module(pkg)
        scanner = venusian.Scanner()
        scanner.scan(module)

        api_router.include_router(
            module.routes.router, tags=tags, prefix=prefix)

        logger.info(f"Loading service <{name}> completed")
        service_descriptions.append({'name': name, 'conf': service_conf})

    fast_app.include_router(views_router, prefix='')
    fast_app.include_router(api_router, prefix=config.API_PREFIX)

    def startup():
        app.state.services = service_descriptions

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("startup", startup)
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    if config.IS_DEBUG:
        logger.info(
            "See http://127.0.0.1:8000/docs for Swagger API Documentation.")

    return fast_app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
