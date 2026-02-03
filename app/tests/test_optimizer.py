# test_optimizer.py
from app.models import Truck, Order, OptimizeRequest
from app.optimizer import optimize
from datetime import date

def test_sample_case():
    truck = Truck(
        id="truck-123",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = [
        Order(
            id="ord-001",
            payout_cents=250000,
            weight_lbs=18000,
            volume_cuft=1200,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 9),
            is_hazmat=False
        ),
        Order(
            id="ord-002",
            payout_cents=180000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 4),
            delivery_date=date(2025, 12, 10),
            is_hazmat=False
        ),
        Order(
            id="ord-003",
            payout_cents=320000,
            weight_lbs=30000,
            volume_cuft=1800,
            origin="Los Angeles, CA",
            destination="Dallas, TX",
            pickup_date=date(2025, 12, 6),
            delivery_date=date(2025, 12, 8),
            is_hazmat=True
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    print(f"Weight: {result.total_weight_lbs} lbs ({result.utilization_weight_percent}%)")
    print(f"Volume: {result.total_volume_cuft} cuft ({result.utilization_volume_percent}%)")
    
    # Expected: ord-001 and ord-002 (total $4,300)
    assert set(result.selected_order_ids) == {"ord-001", "ord-002"}
    assert result.total_payout_cents == 430000

if __name__ == "__main__":
    test_sample_case()
    print("✓ Test passed!")