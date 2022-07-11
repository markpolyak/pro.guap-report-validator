from urllib.request import Request
from fastapi import FastAPI, status
from api.handlers import router, limiter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.schemas import ValidatorResponseBadRequest
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


def get_api() -> FastAPI:
    api = FastAPI()
    api.include_router(router)
    api.state.limiter = limiter
    api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return api


api = get_api()


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Overrides FastAPI default status code for validation errors from 422 to 400."""
    status_json = "error"
    parser = None
    message = str(exc)
    results = []
    response_json = ValidatorResponseBadRequest(
        status=status_json, message=message, parser=parser, results=results)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(response_json),
    )
