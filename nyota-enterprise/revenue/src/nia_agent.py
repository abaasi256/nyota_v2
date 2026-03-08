import asyncio
import os
import json
import asyncpg
from nats.aio.client import Client as NATS
from src.llm_router import router

DB_DSN = os.getenv("DATABASE_URL", "postgresql://os_revenue:os_revenue_pass@nyota_db:5432/nyota_foundation")
NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")

SYSTEM_PROMPT = """You are Nia, the elite AI Sales Representative for Nyota's Revenue OS.
Your objective is to answer client queries about hardware inventory (like RTX GPUs) and push the conversation toward a sale.
Keep your responses concise, professional, and optimized for a WhatsApp interface.
Do NOT use markdown headers or complex formatting. Use plain text with occasional emojis.
Always ask a leading question to keep the lead engaged."""

db_pool = None

async def run():
    global db_pool
    # Initialize DB Pool
    try:
        db_pool = await asyncpg.create_pool(DB_DSN)
        print("Nia connected to Revenue DB (asyncpg).")
    except Exception as e:
        print(f"Nia failed to connect to DB: {e}")
        return

    nc = NATS()
    print("Nia (Revenue AI Agent) connecting to NATS...")
    while True:
        try:
            await nc.connect(NATS_URL)
            break
        except Exception as e:
            await asyncio.sleep(2)
            
    js = nc.jetstream()

    async def handle_message(msg):
        print(f"\n[EVENT] Nia intercepted: {msg.subject}")
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            phone = payload.get("phone_number")
            user_msg = payload.get("message", "")
            
            if user_msg and phone:
                print(f"Processing inbound message from {phone}: {user_msg}")
                
                # Intelligent Escalation Routing
                reply = await router.generate_response(SYSTEM_PROMPT, user_msg)
                
                print(f"[Nia Generated Reply] -> {phone}\n{reply}\n")
                
                # Mock: Here Nia would publish 'events.revenue.message.reply' 
                # which the Moltflow integration would pick up and send to the WhatsApp API.
                
        except Exception as e:
            print(f"Nia encountered an error processing message: {e}")
            
        await msg.ack()

    # Subscribe to incoming WhatsApp messages from the CRM Gateway
    print("Nia is online and listening for inbound leads...")
    await js.subscribe("events.revenue.lead.message", cb=handle_message)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
