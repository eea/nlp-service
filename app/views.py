import fastapi_chameleon
from fastapi import APIRouter, Request
from app.core import config
router = APIRouter()


def get_pipelines(app, service_name):
    services = app.state.services
    service = [s for s in services if s['name'] == service_name][0]
    pipelines = service['conf']['pipelines']

    pipeline_graphs = app.state.pipelines

    out = []

    for pipeline in pipelines:
        pipeline_name = pipeline['name']
        if pipeline_name in pipeline_graphs:
            graph = pipeline_graphs[pipeline_name]
            img = '<img src="data:image/svg+xml;base64,' + \
                graph.decode('ascii') + '" />'
            out.append((pipeline_name, img))

    return out


@router.get('/')
@fastapi_chameleon.template('home.pt')
async def home_post(request: Request):
    return {
        'services': request.app.state.services,
        'app_name': config.APP_NAME,
        'get_pipelines': lambda service_name: get_pipelines(
            request.app, service_name)
    }
