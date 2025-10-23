from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from src.auth.router import router as auth_router
from src.clients.router import router as clients_router
from src.core.config import settings
from src.core.exceptions import AppException
from src.database.events import lifespan
from src.middleware.error_handler import (
    app_exception_handler,
    general_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)
from src.middleware.logging import LoggingMiddleware
from src.tickets.router import router as tickets_router
from src.users.router import router as users_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Mini-CRM for managing repair requests with role-based access",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(clients_router, prefix="/clients", tags=["Clients"])
app.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check",
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
)
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to Repair Requests CRM API",
        "docs": "/docs" if settings.is_development else "Documentation disabled in production",
        "health": "/health",
    }
