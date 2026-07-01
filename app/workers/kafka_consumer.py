import asyncio
import json
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.engine import async_session
from app.models.lead import Lead, LeadStatus
from app.models.inbound import InboundEvent


async def run() -> None:
    consumer = await create_consumer()
    try:
        async for msg in consumer:
            try:
                await process_message(msg.value)
            except Exception as e:
                print(f"[kafka_consumer] Error processing message: {e}")
    finally:
        await consumer.stop()


async def process_message(value: bytes) -> None:
    data = json.loads(value.decode())

    event_id = uuid.UUID(data["event_id"])
    event_type = data["event_type"]
    aggregate_id = uuid.UUID(data["aggregate_id"])
    payload = data["payload"]
    lead_id = uuid.UUID(payload["lead_id"])
    approved = payload["approved"]

    async with async_session() as session:
        existing = await session.execute(
            select(InboundEvent).where(InboundEvent.event_id == event_id)
        )
        if existing.scalar_one_or_none() is not None:
            print(f"[kafka_consumer] Duplicate event {event_id}, skipping")
            return

        inbound = InboundEvent(
            event_id=event_id,
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=data,
        )
        session.add(inbound)

        result = await session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if lead is None:
            print(f"[kafka_consumer] Lead {lead_id} not found, skipping")
            await session.commit()
            return

        lead.status = LeadStatus.approved if approved else LeadStatus.rejected

        await session.commit()
        print(f"[kafka_consumer] Processed event {event_id}, lead {lead_id} -> {lead.status.value}")


async def create_consumer():
    from aiokafka import AIOKafkaConsumer

    consumer = AIOKafkaConsumer(
        settings.KAFKA_MODERATION_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="leads-service",
        auto_offset_reset="earliest",
    )
    await consumer.start()
    return consumer


if __name__ == "__main__":
    asyncio.run(run())
