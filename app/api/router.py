from fastapi import APIRouter

from .routes import heartbeat, questiongeneration

api_router = APIRouter()

# , preprocess, qa, question, search,, summarizer

# api_router.include_router(qa.router, tags=["qa"], prefix="/qa")
# api_router.include_router(search.router, tags=["qa"], prefix="/search")
#
# api_router.include_router(question.router,
#                           tags=["classifier"], prefix="/question")
#
# api_router.include_router(preprocess.router,
#                           tags=["preprocess"], prefix="/preprocess")
# api_router.include_router(summarizer.router,
#                           tags=["preprocess"], prefix="/summary")

api_router.include_router(questiongeneration.router, tags=["preprocess"],
                          prefix="/questiongeneration")

api_router.include_router(heartbeat.router, tags=["health"], prefix="/health")
