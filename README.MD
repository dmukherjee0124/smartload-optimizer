# SmartLoad Optimization API

Optimal truck load planning service using dynamic programming with bitmask optimization.

## How to run
```bash
git clone <your-repo>
cd smartload-optimizer
docker compose up --build
```

Service will be available at http://localhost:8080

## Health check
```bash
curl http://localhost:8080/healthz
```

## Example request
```bash
curl -X POST http://localhost:8080/api/v1/load-optimizer/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "truck": {
      "id": "truck-123",
      "max_weight_lbs": 44000,
      "max_volume_cuft": 3000
    },
    "orders": [
      {
        "id": "ord-001",
        "payout_cents": 250000,
        "weight_lbs": 18000,
        "volume_cuft": 1200,
        "origin": "Los Angeles, CA",
        "destination": "Dallas, TX",
        "pickup_date": "2025-12-05",
        "delivery_date": "2025-12-09",
        "is_hazmat": false
      },
      {
        "id": "ord-002",
        "payout_cents": 180000,
        "weight_lbs": 12000,
        "volume_cuft": 900,
        "origin": "Los Angeles, CA",
        "destination": "Dallas, TX",
        "pickup_date": "2025-12-04",
        "delivery_date": "2025-12-10",
        "is_hazmat": false
      }
    ]
  }'
```

## Algorithm

Uses bitmask dynamic programming (O(2^n)) with the following optimizations:
- Groups orders by route and hazmat compatibility
- Incremental weight/volume calculation using LSB trick
- Time-window feasibility checking
- Early pruning of invalid combinations

Performance: < 800ms for n=22 orders