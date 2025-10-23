import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            },
        )

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"Request completed: {response.status_code} in {process_time:.4f}s",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "path": request.url.path,
            },
        )

        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response
