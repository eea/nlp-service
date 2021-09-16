import fastapi_chameleon
from fastapi import APIRouter, Request

router = APIRouter()


@router.get('/')
@fastapi_chameleon.template('home.pt')
async def home_post(request: Request):
    print(request.app.state.services)
    import pdb
    pdb.set_trace()
    return {}
