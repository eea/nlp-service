from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.qa import QA_Request, Response
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=Response)
def query(payload: QA_Request, request: Request):
    if payload.use_dp:
        model = request.app.state.dp_qa
    else:
        model = request.app.state.qa
    with concurrency_limiter.run():
        import pdb
        pdb.set_trace()
        return model.predict(payload)
