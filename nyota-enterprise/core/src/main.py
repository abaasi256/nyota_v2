import asyncio
import os
import json
from uuid import uuid4
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError

app = FastAPI(title="Nyota Core Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nats_client = NATS()
js = None

class EventPayload(BaseModel):
    action: str
    target: str
    data: dict

async def connect_nats():
    global js
    nats_url = os.getenv("NATS_URL", "nats://nyota_bus:4222")
    await nats_client.connect(nats_url)
    js = nats_client.jetstream()
    
    # Ensure stream exists
    try:
        await js.stream_info("ENTERPRISE_EVENTS")
    except NotFoundError:
        await js.add_stream(name="ENTERPRISE_EVENTS", subjects=["events.>"])
    
    print("Connected to NATS JetStream")

@app.on_event("startup")
async def startup_event():
    while True:
        try:
            await connect_nats()
            break
        except Exception as e:
            print(f"Failed to connect to NATS, retrying in 2 seconds... {e}")
            await asyncio.sleep(2)

@app.on_event("shutdown")
async def shutdown_event():
    await nats_client.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "nats_connected": nats_client.is_connected}

@app.post("/bus/publish/{domain}/{subdomain}")
async def publish_event(domain: str, subdomain: str, payload: EventPayload):
    subject = f"events.{domain}.{subdomain}.{payload.action}"
    
    envelope = {
        "event_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0",
        "source": "os.core.gateway",
        "domain": domain,
        "priority": "HIGH",
        "trace_id": str(uuid4()),
        "payload": payload.data
    }
    
    try:
        ack = await js.publish(subject, json.dumps(envelope).encode())
        return {"status": "published", "subject": subject, "seq": ack.seq}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    
    queue = asyncio.Queue()
    async def nats_handler(msg):
        await queue.put(msg)
        
    sub = await nats_client.subscribe("events.>", cb=nats_handler)
    
    async def forward_messages():
        while True:
            msg = await queue.get()
            try:
                payload = json.loads(msg.data.decode())
            except Exception:
                payload = str(msg.data)
                
            try:
                await websocket.send_json({
                    "subject": msg.subject,
                    "data": payload
                })
            except Exception:
                break
                
    sender_task = asyncio.create_task(forward_messages())
    
    try:
        while True:
            # Keep connection open and detect disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    finally:
        sender_task.cancel()
        await sub.unsubscribe()
