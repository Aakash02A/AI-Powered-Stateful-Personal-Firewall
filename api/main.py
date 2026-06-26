import asyncio
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.config import settings
from api.routes import analytics, health, logs, ws

# Setup standard logging
logger = logging.getLogger("api")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
ch = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(
        f"Starting Personal Firewall API v1.0.0 on {settings.HOST}:{settings.PORT}",
        extra={"request_id": "system"},
    )

    # Start WebSocket background broadcaster
    import api.routes.ws as ws_module

    ws_module.broadcast_task = asyncio.create_task(ws_module.broadcast_events())

    yield

    # Shutdown
    logger.info("Initiating graceful shutdown sequence", extra={"request_id": "system"})
    if ws_module.broadcast_task:
        ws_module.broadcast_task.cancel()

    # Flush database writer and stop capture thread if running in unified mode
    import firewall.cli as fw_cli

    if hasattr(fw_cli, "fw_instance") and fw_cli.fw_instance is not None:
        logger.info("Stopping Firewall daemon...", extra={"request_id": "system"})
        fw_cli.fw_instance.stop()

    logger.info("Shutdown complete", extra={"request_id": "system"})


app = FastAPI(
    title="Personal Firewall API",
    description="REST and WebSocket API for the AI-Powered Stateful Personal Firewall",
    version="1.0.0",
    lifespan=lifespan,
)

# Instrument Prometheus Metrics
Instrumentator().instrument(app).expose(app)

# Exception Handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid request parameters",
            "details": exc.errors(),
        },
    )


# Middleware
@app.middleware("http")
async def add_security_headers_and_log(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.time()
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={"request_id": request_id},
    )

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            f"Request failed: {e}", extra={"request_id": request_id}, exc_info=True
        )
        raise

    process_time = (time.time() - start_time) * 1000

    # Security Headers
    response.headers["X-Request-ID"] = request_id
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    logger.info(
        f"Response status: {response.status_code} - Process time: {process_time:.2f}ms",
        extra={
            "request_id": request_id,
            "process_time_ms": process_time,
            "status_code": response.status_code,
        },
    )
    return response


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analytics.router)
app.include_router(logs.router)
app.include_router(ws.router)
app.include_router(health.router)


@app.get("/")
@limiter.limit(settings.RATE_LIMIT)
def read_root(request: Request):
    return {
        "message": "Welcome to the Personal Firewall API. Visit /docs for documentation."
    }


@app.get("/version", summary="Application Version")
def version():
    commit_hash = os.getenv("GIT_COMMIT_HASH", "unknown")
    build_date = os.getenv("BUILD_DATE", "unknown")
    return {
        "version": app.version,
        "commit_hash": commit_hash,
        "build_date": build_date,
    }
