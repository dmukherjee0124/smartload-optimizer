from __future__ import annotations

from datetime import date
from typing import List
from pydantic import BaseModel, Field, validator


class Truck(BaseModel):
    id: str
    max_weight_lbs: int = Field(..., ge=0)
    max_volume_cuft: int = Field(..., ge=0)


class Order(BaseModel):
    id: str
    payout_cents: int = Field(..., ge=0)
    weight_lbs: int = Field(..., ge=0)
    volume_cuft: int = Field(..., ge=0)
    origin: str
    destination: str
    pickup_date: date
    delivery_date: date
    is_hazmat: bool

    @validator("delivery_date")
    @classmethod
    def delivery_not_before_pickup(cls, v: date, values):
        pickup = values.get("pickup_date")
        if pickup is not None and v < pickup:
            raise ValueError("delivery_date must be >= pickup_date")
        return v


class OptimizeRequest(BaseModel):
    truck: Truck
    orders: List[Order] = Field(default_factory=list)


class OptimizeResponse(BaseModel):
    truck_id: str
    selected_order_ids: List[str]
    total_payout_cents: int
    total_weight_lbs: int
    total_volume_cuft: int
    utilization_weight_percent: float
    utilization_volume_percent: float