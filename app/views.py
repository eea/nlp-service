import fastapi_chameleon
from fastapi import APIRouter, Request
from app.core import config
router = APIRouter()


@router.get('/')
@fastapi_chameleon.template('home.pt')
async def home_post(request: Request):
    return {
        'services': request.app.state.services,
        'app_name': config.APP_NAME
    }
