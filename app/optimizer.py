from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple

from .models import Order, Truck, OptimizeResponse


def _date2i(d: date) -> int:
    """
    Convert date to a comparable integer.
    Using date.toordinal() keeps comparisons fast and avoids timezone pitfalls.
    """
    return d.toordinal()


@dataclass(frozen=True)
class BestResult:
    """
    Simple immutable holder for the best solution found in a group.
    """
    payout: int
    weight: int
    volume: int
    selected_ids: Tuple[str, ...]


def _round2(x: float) -> float:
    return round(x + 1e-12, 2)


def optimize(truck: Truck, orders: List[Order]) -> OptimizeResponse:
    """
    Optimize by selecting a subset of orders that maximizes payout_cents while:
      - staying within truck weight/volume
      - respecting compatibility (route, hazmat isolation, time-window overlap)

    Approach:
      - n is small (<= ~22), so a bitmask DP over subsets is practical.
      - To reduce work further, we group orders by (origin, destination, is_hazmat),
        because different lanes and hazmat/non-hazmat can't be mixed.
    """
    if not orders:
        return OptimizeResponse(
            truck_id=truck.id,
            selected_order_ids=[],
            total_payout_cents=0,
            total_weight_lbs=0,
            total_volume_cuft=0,
            utilization_weight_percent=0.0,
            utilization_volume_percent=0.0,
        )

    # Grouping enforces:
    #  - same lane (origin->destination)
    #  - hazmat isolation (hazmat vs non-hazmat not mixed)
    groups: Dict[Tuple[str, str, bool], List[Order]] = {}
    for o in orders:
        key = (o.origin, o.destination, o.is_hazmat)
        groups.setdefault(key, []).append(o)

    best = BestResult(payout=0, weight=0, volume=0, selected_ids=())

    for (_origin, _dest, _haz), grp in groups.items():
        # ~20-22 orders approx
        if len(grp) > 22:
            grp = grp[:22]

        candidate = _best_subset_for_group(truck, grp)
        if candidate.payout > best.payout:
            best = candidate

    util_w = (best.weight / truck.max_weight_lbs * 100.0) if truck.max_weight_lbs else 0.0
    util_v = (best.volume / truck.max_volume_cuft * 100.0) if truck.max_volume_cuft else 0.0

    return OptimizeResponse(
        truck_id=truck.id,
        selected_order_ids=list(best.selected_ids),
        total_payout_cents=int(best.payout),
        total_weight_lbs=int(best.weight),
        total_volume_cuft=int(best.volume),
        utilization_weight_percent=_round2(util_w),
        utilization_volume_percent=_round2(util_v),
    )


def _best_subset_for_group(truck: Truck, grp: List[Order]) -> BestResult:
    """
    Bitmask DP for one compatible group (same lane + same hazmat flag).

    bitmask:
      - represent a subset of m orders as an integer mask in [0, 2^m).
      - if bit i is 1 -> order i is included.

    Incremental trick:
      - For each mask, take its lowest set bit (LSB) and build mask from prev = mask ^ LSB.
      - That makes totals O(1) per mask instead of re-summing items.
    """
    m = len(grp)
    if m == 0:
        return BestResult(payout=0, weight=0, volume=0, selected_ids=())

    ids = [o.id for o in grp]
    payout = [o.payout_cents for o in grp]
    weight = [o.weight_lbs for o in grp]
    volume = [o.volume_cuft for o in grp]
    pickup = [_date2i(o.pickup_date) for o in grp]
    delivery = [_date2i(o.delivery_date) for o in grp]

    size = 1 << m
    w = [0] * size
    v = [0] * size
    p = [0] * size

    # Time-window aggregation:
    #   max pickup across chosen orders
    #   min delivery across chosen orders
    # Feasible if max_pickup <= min_delivery (there exists an overlap window).
    max_pick = [0] * size
    INF = 10**18
    min_del = [INF] * size
    min_del[0] = INF
    max_pick[0] = 0

    best_mask = 0
    best_payout = 0
    best_weight = 0
    best_volume = 0

    for mask in range(1, size):
        lsb = mask & -mask
        j = (lsb.bit_length() - 1)  # index of the added order
        prev = mask ^ lsb

        ww = w[prev] + weight[j]
        vv = v[prev] + volume[j]
        pp = p[prev] + payout[j]

        w[mask] = ww
        v[mask] = vv
        p[mask] = pp

        # Update max pickup / min delivery
        mp_prev = max_pick[prev]
        pj = pickup[j]
        max_pick[mask] = pj if pj > mp_prev else mp_prev

        md_prev = min_del[prev]
        dj = delivery[j]
        min_del[mask] = dj if dj < md_prev else md_prev

        # Capacity prune
        if ww > truck.max_weight_lbs or vv > truck.max_volume_cuft:
            continue

        # Time-window overlap prune
        if max_pick[mask] > min_del[mask]:
            continue

        if pp > best_payout:
            best_payout = pp
            best_mask = mask
            best_weight = ww
            best_volume = vv

    # Decode best_mask into ids
    selected = []
    mm = best_mask
    idx = 0
    while mm:
        if mm & 1:
            selected.append(ids[idx])
        mm >>= 1
        idx += 1

    return BestResult(
        payout=best_payout,
        weight=best_weight,
        volume=best_volume,
        selected_ids=tuple(selected),
    )
