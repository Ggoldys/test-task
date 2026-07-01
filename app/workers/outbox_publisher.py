import asyncio
import json
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.engine import async_session
from app.models.outbox import OutboxEvent


async def run() -> None:
    while True:
        try:
            await process_outbox()
        except Exception as e:
            print(f"[outbox_publisher] Error: {e}")
        await asyncio.sleep(settings.OUTBOX_POLL_INTERVAL)


async def process_outbox() -> None:
    async with async_session() as session:
        result = await session.execute(
            select(OutboxEvent).where(OutboxEvent.published == False).order_by(OutboxEvent.created_at).limit(50)
        )
        events = result.scalars().all()

        if not events:
            return

        producer = await create_producer()
        try:
            for event in events:
                try:
                    value = {
                        "event_id": str(event.id),
                        "event_type": event.event_type,
                        "aggregate_id": str(event.aggregate_id),
                        "occurred_at": event.created_at.isoformat(),
                        "payload": event.payload,
                    }

                    await producer.send_and_wait(
                        settings.KAFKA_LEADS_TOPIC,
                        value=json.dumps(value, default=str).encode(),
                        key=str(event.aggregate_id).encode(),
                    )

                    await session.execute(
                        update(OutboxEvent)
                        .where(OutboxEvent.id == event.id)
                        .values(published=True)
                    )
                    await session.commit()
                    print(f"[outbox_publisher] Published event {event.id}")
                except Exception as e:
                    await session.rollback()
                    print(f"[outbox_publisher] Failed to publish event {event.id}: {e}")
        finally:
            await producer.stop()


async def create_producer():
    from aiokafka import AIOKafkaProducer

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    await producer.start()
    return producer


if __name__ == "__main__":
    asyncio.run(run())
