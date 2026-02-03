# SmartLoad Optimization API

Optimal truck load planning service using dynamic programming with bitmask optimization.

## How to run
```bash
git clone <repo>
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
curl -X POST http://localhost:8080/api/v1/load-optimizer/optimize -H "Content-Type: application/json" -d @sample-request.json
```

## Run tests
```bash
docker compose run api python -m app.tests.test_optimizer  
```
## Algorithm

Uses bitmask dynamic programming (O(2^n)) with the following optimizations:
- Groups orders by route and hazmat compatibility
- Incremental weight/volume calculation using LSB trick
- Time-window feasibility checking
- Early pruning of invalid combinations

Performance: < 800ms for n=22 orders