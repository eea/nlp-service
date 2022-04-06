from importlib.metadata import version

from fastapi import APIRouter

router = APIRouter()


@router.get("/initialized")
def check_status():
    """
    This endpoint can be used during startup to understand if the
    server is ready to take any requests, or is still loading.

    The recommended approach is to call this endpoint with a short timeout,
    like 500ms, and in case of no reply, consider the server busy.
    """
    return True


@router.get("/version")
def get_version():
    """
    Get the running Haystack version.
    """
    return {"version": version("NLPService")}
