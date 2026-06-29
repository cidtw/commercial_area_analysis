import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router
from app.adapters.geo.errors import GeoProviderError
from app.bootstrap.mock_seed import ensure_mock_seeded
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        session = SessionLocal()
        try:
            ensure_mock_seeded(session)
        finally:
            session.close()
    yield


app = FastAPI(title="Commercial Area Analysis API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_error_response(
    *,
    status_code: int,
    error: str,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "error": error,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(LookupError)
async def handle_lookup_error(_: Request, exc: LookupError) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        error="Not Found",
        message=str(exc),
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error="Validation Error",
        message="Request validation failed.",
        details=exc.errors(),
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code in HTTPStatus._value2member_map_:
        phrase = HTTPStatus(exc.status_code).phrase
    else:
        phrase = "HTTP Error"
    message = exc.detail if isinstance(exc.detail, str) else phrase
    return build_error_response(
        status_code=exc.status_code,
        error=phrase,
        message=message,
    )


@app.exception_handler(SQLAlchemyError)
async def handle_sqlalchemy_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("database request failed", exc_info=exc)
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="Database Error",
        message="A database operation failed.",
    )


@app.exception_handler(GeoProviderError)
async def handle_geo_provider_error(_: Request, exc: GeoProviderError) -> JSONResponse:
    return build_error_response(
        status_code=exc.status_code,
        error="Geo Provider Error",
        message=str(exc),
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unexpected request failure", exc_info=exc)
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="Internal Server Error",
        message="An unexpected server error occurred.",
    )


app.include_router(router)
