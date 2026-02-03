from fastapi import FastAPI, Request
from app.models import OptimizeRequest
from app.optimizer import optimize as run_optimizer
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

MAX_BODY_BYTES = 1_000_000  # 1 MB


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Payload too large"})
    request._body = body  # cache body so downstream can read it
    return await call_next(request)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/v1/load-optimizer/optimize")
def optimize(req: OptimizeRequest):
    # Step 4: algorithm-only implementation (validation + caching come next)
    return run_optimizer(req.truck, req.orders)
