from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from deps import require_role
from services.pickup_points import create_pickup_point, get_pickup_points_filtered

router = APIRouter(prefix="/pickup-points", tags=["Pickup Points"])

class PickupPointCreate(BaseModel):
    city: str
class PickupPointOut(BaseModel):
    id: int
    city: str
    created_at: datetime
@router.post("/", response_model=PickupPointOut, dependencies=[Depends(require_role("moderator"))])
async def add_pickup_point(data: PickupPointCreate):
    return await create_pickup_point(data.city)
@router.get("/", response_model=List[PickupPointOut], dependencies=[Depends(require_role("moderator"))])
async def list_pickup_points(
    from_date: datetime = Query(..., description="Начало диапазона по дате приёмки"),
    to_date: datetime = Query(..., description="Конец диапазона по дате приёмки"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await get_pickup_points_filtered(from_date, to_date, limit, offset)
