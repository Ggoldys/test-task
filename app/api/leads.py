import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session
from app.schemas.lead import LeadCreate, LeadResponse
from app.services import lead as lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    data: LeadCreate,
    session: AsyncSession = Depends(get_session),
):
    correlation_id = str(uuid.uuid4())
    lead = await lead_service.create_lead(session, data, correlation_id)
    await session.commit()
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    correlation_id = str(uuid.uuid4())
    lead = await lead_service.get_lead(session, lead_id, correlation_id)
    return lead
