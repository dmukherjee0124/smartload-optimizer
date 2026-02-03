from fastapi import FastAPI
from app.models import OptimizeRequest
from app.optimizer import optimize as run_optimizer

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/v1/load-optimizer/optimize")
def optimize(req: OptimizeRequest):
    # Step 4: algorithm-only implementation (validation + caching come next)
    return run_optimizer(req.truck, req.orders)
