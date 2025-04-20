from fastapi import APIRouter, Depends
from pydantic import BaseModel
from deps import require_role
from services.intakes import create_intake
from services.intakes import close_intake

router = APIRouter(prefix="/intakes", tags=["Intakes"])

class IntakeCreate(BaseModel):
    pickup_point_id: int

@router.post("/", dependencies=[Depends(require_role("moderator"))])
async def add_intake(data: IntakeCreate):
    return await create_intake(data.pickup_point_id)
@router.post("/{intake_id}/close", dependencies=[Depends(require_role("moderator"))])
async def close_intake_endpoint(intake_id: int):
    return await close_intake(intake_id)
