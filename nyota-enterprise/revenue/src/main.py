import asyncio
import os
import json
import psycopg2
from uuid import uuid4
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from nats.aio.client import Client as NATS
from pydantic import BaseModel

app = FastAPI(title="Nyota Revenue OS - CRM Gateway", version="2.0.0")

DB_DSN = os.getenv("DATABASE_URL", "postgresql://os_revenue:os_revenue_pass@nyota_db:5432/nyota_foundation")
NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")
nats_client = NATS()
js = None

def init_crm_lead(phone_number):
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO revenue.leads (phone_number, status)
            VALUES (%s, 'NEW')
            ON CONFLICT (phone_number) DO UPDATE SET last_interaction = CURRENT_TIMESTAMP
            RETURNING id, status;
            """,
            (phone_number,)
        )
        lead = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return lead
    except Exception as e:
        print(f"Failed to upsert lead to postgres: {e}")
        return None

async def connect_nats():
    global js
    await nats_client.connect(NATS_URL)
    js = nats_client.jetstream()
    print("Revenue OS Connected to NATS JetStream")

@app.on_event("startup")
async def startup_event():
    while True:
        try:
            await connect_nats()
            break
        except Exception as e:
            print(f"Waiting for NATS: {e}")
            await asyncio.sleep(2)

@app.on_event("shutdown")
async def shutdown_event():
    await nats_client.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "nats_connected": nats_client.is_connected}

@app.post("/webhook/moltflow")
async def moltflow_webhook(request: Request):
    """
    Ingests callbacks from WhatsApp Moltflow automation and routes them to the Event Bus.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Very basic validation of Moltflow structure
    sender = payload.get("sender_phone", "unknown")
    message = payload.get("message_body", "")
    
    # Persist locally in CRM immediately (Synchronous State)
    if sender != "unknown":
        lead = init_crm_lead(sender)
        print(f"Upserted lead status for {sender}: {lead}")

    # Build Event to trigger workflows asynchronously
    event_payload = {
        "event_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domain": "revenue",
        "source": "os.revenue.moltflow",
        "action": "webhook_received",
        "payload": {
            "phone_number": sender,
            "message": message,
            "channel": "whatsapp"
        }
    }
    
    try:
        subject = "events.revenue.lead.message"
        ack = await js.publish(subject, json.dumps(event_payload).encode())
        return {"status": "processed", "seq": ack.seq}
    except Exception as e:
        print(f"NATS Publish Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to route event to Swarm")
