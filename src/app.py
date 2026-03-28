from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from src.api.api import router
from src.utils.logger import logger


def create_fast_api_app() -> FastAPI:
    logger.debug("Initializing FastAPI application")
    app = FastAPI(
        title="Prasaarit Upload Service",
        description="Upload service for Prasaarit",
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"error": exc.errors()})

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        logger.error(f"Missing environment variable: {exc}")
        return JSONResponse(
            status_code=500, content={"error": "Server configuration error"}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

    app.include_router(router)

    return app
