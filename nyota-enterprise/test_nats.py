import asyncio
import json
from nats.aio.client import Client as NATS

async def run():
    nc = NATS()
    print("Connecting to NATS...")
    await nc.connect("nats://localhost:4222") # Localhost since we're outside docker
    js = nc.jetstream()
    
    # Create the persistent stream if it doesn't exist
    try:
        await js.add_stream(name="ENTERPRISE_EVENTS", subjects=["events.>"])
        print("Stream ENTERPRISE_EVENTS configured.")
    except Exception as e:
        print("Note: Stream might already exist or eror:", e)

    async def message_handler(msg):
        print(f"SECURITY OS (Listener) RECEIVED: [{msg.subject}] : {msg.data.decode()}")
        await msg.ack()

    # Subscribe to ALL events
    print("Listening on events.>")
    sub = await js.subscribe("events.>", cb=message_handler)
    
    # Wait a moment for subscriber to be ready
    await asyncio.sleep(1)

    print("Publishing boot event...")
    payload = json.dumps({
        "event_id": "test-uuid-001",
        "action": "boot_sequence",
        "status": "online"
    }).encode()
    
    ack = await js.publish("events.core.system.booted", payload)
    print(f"Ack received: {ack}")
    
    print("Waiting for echo back...")
    await asyncio.sleep(2)
    await nc.close()

if __name__ == '__main__':
    asyncio.run(run())
