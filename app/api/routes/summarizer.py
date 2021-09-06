from app.core.config import CONCURRENT_REQUEST_PER_WORKER
from app.core.utils import RequestLimiter
from app.data_models.summarizer import SummaryRequest, SummaryResponse
from fastapi import APIRouter, Request

router = APIRouter()

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.post("/query", response_model=SummaryResponse)
def query(payload: SummaryRequest, request: Request):
    model = request.app.state.summarizer_model

    def _post_process(self, prediction):
        import pdb
        pdb.set_trace()
        # output_1 is Question
        # output_2 is Keyword
        return {"answer": prediction['category']}

    with concurrency_limiter.run():
        return model.predict(payload)
