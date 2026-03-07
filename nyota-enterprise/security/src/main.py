import asyncio
import os
import json
import psycopg2
from nats.aio.client import Client as NATS

DB_DSN = os.getenv("DATABASE_URL", "postgresql://os_security:os_sec_pass@nyota_db:5432/nyota_foundation")
NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")

def log_to_postgres(event_id, domain, topic, payload):
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO security.nats_audit_log (event_id, domain, topic, payload)
            VALUES (%s, %s, %s, %s)
            """,
            (event_id, domain, topic, json.dumps(payload))
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to log to postgres: {e}")
        return False

async def run():
    nc = NATS()
    print(f"Connecting to {NATS_URL}")
    while True:
        try:
            await nc.connect(NATS_URL)
            break
        except Exception as e:
            print(f"Waiting for NATS: {e}")
            await asyncio.sleep(2)
            
    js = nc.jetstream()
    
    async def message_handler(msg):
        print(f"SECURITY OS RECEIVED: [{msg.subject}]")
        try:
            data = json.loads(msg.data.decode())
            event_id = data.get("event_id", "unknown")
            domain = data.get("domain", "unknown")
            
            # Log to DB
            if log_to_postgres(event_id, domain, msg.subject, data):
                print(f"  -> Logged event {event_id} to DB")
            
        except json.JSONDecodeError:
            print("  -> Invalid JSON payload")
            
        await msg.ack()

    print("Baraka Validator: Subscribing to events.>")
    await js.subscribe("events.>", cb=message_handler)

    print("Security OS is now running and protecting the network...")
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
