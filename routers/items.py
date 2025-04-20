from fastapi import APIRouter, Depends
from pydantic import BaseModel
from deps import require_role
from services.items import create_item, delete_last_item_from_open_intake

router = APIRouter(prefix="/items", tags=["Items"])


class ItemCreate(BaseModel):
    type: str
    pickup_point_id: int  # теперь передаём ПВЗ, а не intake_id

@router.post("/", dependencies=[Depends(require_role("employee_pvz"))])
async def add_item(data: ItemCreate):
    return await create_item(data.type, data.pickup_point_id)
@router.delete("/pickup_point/{pickup_point_id}/last", dependencies=[Depends(require_role("employee_pvz"))])
async def delete_last_item(pickup_point_id: int):
    return await delete_last_item_from_open_intake(pickup_point_id)
