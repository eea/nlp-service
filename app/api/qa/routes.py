from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from fastapi import APIRouter, Request

from .api import QA_Request, Response

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("", response_model=Response)
def query(payload: QA_Request, request: Request):
    params = payload.dict()["params"]
    if params.get("use_dp"):
        qa_model = request.app.state.dp_qa
    else:
        qa_model = request.app.state.qa

    with concurrency_limiter.run():
        stage_1 = qa_model.predict(payload.dict())

    return stage_1

    # return {
    #     "query": stage_1["query"],
    #     "answers": stage_1["answers"],
    # }
    # stage_2 = request.app.state.similarity_model.clusterize_answers(stage_1)
    #
    # # desired output in clusterized:
    #
    # return stage_2
