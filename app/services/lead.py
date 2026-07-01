import uuid
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadStatus
from app.models.outbox import OutboxEvent
from app.schemas.lead import LeadCreate
from app.core.exceptions import LeadNotFoundException


async def create_lead(session: AsyncSession, data: LeadCreate, correlation_id: str) -> Lead:
    lead = Lead(
        name=data.name,
        phone=data.phone,
        source=data.source,
        comment=data.comment,
        status=LeadStatus.new,
    )
    session.add(lead)
    await session.flush()

    event = OutboxEvent(
        event_type="lead_created.v1",
        aggregate_id=lead.id,
        payload={
            "lead_id": str(lead.id),
            "name": lead.name,
            "phone": lead.phone,
            "source": lead.source,
        },
    )
    session.add(event)

    return lead


async def get_lead(session: AsyncSession, lead_id: uuid.UUID, correlation_id: str) -> Lead:
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if lead is None:
        raise LeadNotFoundException(str(lead_id), correlation_id)

    return lead
