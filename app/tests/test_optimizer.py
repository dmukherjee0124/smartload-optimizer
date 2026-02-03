# test_optimizer.py
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models import Truck, Order
from app.optimizer import optimize
from datetime import date


def test_sample_case():
    """Test the sample case from the problem statement"""
    print("\n=== Test 1: Sample Case ===")
    
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
    assert result.total_weight_lbs == 30000
    assert result.total_volume_cuft == 2100
    print("✓ Test passed!")


def test_empty_orders():
    """Test with no orders"""
    print("\n=== Test 2: Empty Orders ===")
    
    truck = Truck(
        id="truck-456",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = []
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    assert result.selected_order_ids == []
    assert result.total_payout_cents == 0
    assert result.total_weight_lbs == 0
    assert result.total_volume_cuft == 0
    assert result.utilization_weight_percent == 0.0
    assert result.utilization_volume_percent == 0.0
    print("✓ Test passed!")


def test_single_order():
    """Test with a single order that fits"""
    print("\n=== Test 3: Single Order ===")
    
    truck = Truck(
        id="truck-789",
        max_weight_lbs=44000,
        max_volume_cuft=3000
    )
    
    orders = [
        Order(
            id="ord-single",
            payout_cents=500000,
            weight_lbs=20000,
            volume_cuft=1500,
            origin="New York, NY",
            destination="Boston, MA",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 3),
            is_hazmat=False
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    assert result.selected_order_ids == ["ord-single"]
    assert result.total_payout_cents == 500000
    print("✓ Test passed!")


def test_over_capacity():
    """Test with orders that exceed truck capacity"""
    print("\n=== Test 4: All Orders Over Capacity ===")
    
    truck = Truck(
        id="truck-small",
        max_weight_lbs=10000,
        max_volume_cuft=500
    )
    
    orders = [
        Order(
            id="ord-heavy-1",
            payout_cents=300000,
            weight_lbs=15000,
            volume_cuft=800,
            origin="Chicago, IL",
            destination="Detroit, MI",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 3),
            is_hazmat=False
        ),
        Order(
            id="ord-heavy-2",
            payout_cents=400000,
            weight_lbs=20000,
            volume_cuft=1000,
            origin="Chicago, IL",
            destination="Detroit, MI",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 3),
            is_hazmat=False
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    # No orders should fit
    assert result.selected_order_ids == []
    assert result.total_payout_cents == 0
    print("✓ Test passed!")


def test_hazmat_isolation():
    """Test that hazmat and non-hazmat orders are not mixed"""
    print("\n=== Test 5: Hazmat Isolation ===")
    
    truck = Truck(
        id="truck-hazmat",
        max_weight_lbs=50000,
        max_volume_cuft=4000
    )
    
    orders = [
        Order(
            id="ord-regular",
            payout_cents=200000,
            weight_lbs=10000,
            volume_cuft=800,
            origin="Atlanta, GA",
            destination="Miami, FL",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 5),
            is_hazmat=False
        ),
        Order(
            id="ord-hazmat-1",
            payout_cents=300000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Atlanta, GA",
            destination="Miami, FL",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 5),
            is_hazmat=True
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    # Should select the hazmat order (higher payout)
    # Hazmat and non-hazmat should not be mixed
    assert result.total_payout_cents == 300000
    assert "ord-hazmat-1" in result.selected_order_ids
    assert "ord-regular" not in result.selected_order_ids
    print("✓ Test passed!")


def test_different_routes():
    """Test that orders with different routes are not mixed"""
    print("\n=== Test 6: Different Routes ===")
    
    truck = Truck(
        id="truck-routes",
        max_weight_lbs=50000,
        max_volume_cuft=4000
    )
    
    orders = [
        Order(
            id="ord-route-1",
            payout_cents=200000,
            weight_lbs=10000,
            volume_cuft=800,
            origin="Seattle, WA",
            destination="Portland, OR",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 3),
            is_hazmat=False
        ),
        Order(
            id="ord-route-2",
            payout_cents=250000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Denver, CO",
            destination="Phoenix, AZ",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 3),
            is_hazmat=False
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    # Should select only one route (the higher paying one)
    assert len(result.selected_order_ids) == 1
    assert result.total_payout_cents == 250000
    print("✓ Test passed!")


def test_time_window_conflict():
    """Test that orders with conflicting time windows are handled"""
    print("\n=== Test 7: Time Window Conflict ===")
    
    truck = Truck(
        id="truck-time",
        max_weight_lbs=50000,
        max_volume_cuft=4000
    )
    
    orders = [
        Order(
            id="ord-early",
            payout_cents=200000,
            weight_lbs=10000,
            volume_cuft=800,
            origin="Houston, TX",
            destination="San Antonio, TX",
            pickup_date=date(2025, 12, 1),
            delivery_date=date(2025, 12, 2),
            is_hazmat=False
        ),
        Order(
            id="ord-late",
            payout_cents=250000,
            weight_lbs=12000,
            volume_cuft=900,
            origin="Houston, TX",
            destination="San Antonio, TX",
            pickup_date=date(2025, 12, 5),
            delivery_date=date(2025, 12, 6),
            is_hazmat=False
        )
    ]
    
    result = optimize(truck, orders)
    
    print(f"Selected: {result.selected_order_ids}")
    print(f"Total payout: ${result.total_payout_cents / 100:.2f}")
    
    # These orders don't overlap in time, so they can't be combined
    # Should select the higher paying one
    assert len(result.selected_order_ids) == 1
    print("✓ Test passed!")


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("Running SmartLoad Optimizer Tests")
    print("=" * 60)
    
    tests = [
        test_sample_case,
        test_empty_orders,
        test_single_order,
        test_over_capacity,
        test_hazmat_isolation,
        test_different_routes,
        test_time_window_conflict,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)