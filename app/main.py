from fastapi import FastAPI
from app.models import OptimizeRequest

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/v1/load-optimizer/optimize")
def optimize(req: OptimizeRequest):
    return {
        "truck_id": req.truck.id,
        "selected_order_ids": [],
        "total_payout_cents": 0,
        "total_weight_lbs": 0,
        "total_volume_cuft": 0,
        "utilization_weight_percent": 0.0,
        "utilization_volume_percent": 0.0
    }

