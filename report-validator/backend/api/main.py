from fastapi import Body, FastAPI, status
from api.handlers import router
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.schemas import ValidatorResponseBadRequest


def get_api() -> FastAPI:
    api = FastAPI()
    api.include_router(router)
    return api


api = get_api()


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Overrides FastAPI default status code for validation errors from 422 to 400."""
    status_json = "error"
    parser = None
    message = exc.errors()
    results = []
    response_json = ValidatorResponseBadRequest(
        status=status_json, message=message, parser=parser, results=results)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(response_json),
    )
