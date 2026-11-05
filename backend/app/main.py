import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.api.v1 import (
    health,
    invoices,
    documents,
    extractions,
    matching,
    exceptions,
    approvals,
    payment_ready,
    audit,
    vendors,
    demo,
    switch_rooms,
    telegram_gateway,
)
from backend.app.services.seed_service import seed_database
from backend.app.services.telegram_service import telegram_gateway as tg_service
from backend.app.models.all_models import Invoice

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Auto-seed if database is empty
with SessionLocal() as db:
    if db.query(Invoice).count() == 0:
        try:
            seed_database(db, run_initial_match=True)
        except Exception:
            pass
    if db.query(Invoice).filter(Invoice.id == "I-2001").count() == 0:
        try:
            from backend.app.services.ap_data_loader import feed_ap_data
            feed_ap_data(db, run_matches=True)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Telegram Gateway polling in background if configured
    if settings.TELEGRAM_GATEWAY_ENABLED and settings.TELEGRAM_POLLING:
        tg_service.start_polling_in_background()
    yield
    # Shutdown: Cleanly cancel polling task
    tg_service.stop_polling()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="InvoiceOps API - Collaborative Autonomous AP Exception Resolution & 3-Way Matching Engine",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
    request.state.request_id = req_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# Error Handlers adhering strictly to Error Envelope
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    error_dict = {"code": "HTTP_ERROR", "message": exc.detail, "details": []}

    if isinstance(exc.detail, dict) and "error" in exc.detail:
        error_dict = exc.detail["error"]
    elif isinstance(exc.detail, dict):
        error_dict = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_dict, "request_id": req_id},
        headers={"X-Request-ID": req_id},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    errors = exc.errors()
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": details,
            },
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )

# Include Routers under /api/v1
app.include_router(health.router, prefix="/api/v1")
app.include_router(health.router, prefix="") # support /health at root
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(extractions.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(exceptions.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(payment_ready.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(vendors.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")
app.include_router(switch_rooms.router, prefix="/api/v1")
app.include_router(telegram_gateway.router, prefix="/api/v1")

# Mount built frontend SPA if available (checks repo root, backend root, and fallback mirrors)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

possible_dist_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend_dist")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist")),
]
frontend_dist = next((d for d in possible_dist_dirs if os.path.exists(d) and os.path.isdir(d)), None)

if frontend_dist:
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        response = FileResponse(os.path.join(frontend_dist, "index.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
