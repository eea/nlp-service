from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import SearchRequest

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("")
def query(payload: SearchRequest, request: Request):
    body = payload.dict()
    use_dp = body["params"].pop("use_dp", False)
    body.update(body.get("params", {}) or {})
    source = body.pop("source", None)

    # pydantic doesn't like fields with _underscore in beginning?
    # See https://github.com/samuelcolvin/pydantic/issues/288 for possible fixes
    if source:
        body["_source"] = source

    if use_dp:
        model = request.app.state.dp_search
    else:
        model = request.app.state.search

    with concurrency_limiter.run():
        result = model.predict(body)
        return result


# @router.get("/graph")
# def graph(request: Request, response: Response):
#     model = request.app.state.search
#     pipeline = model.pipeline
#
#     img = pipeline.draw(path=None)
#     response.headers['Content-Type'] = 'image/png'
#
#     return img
