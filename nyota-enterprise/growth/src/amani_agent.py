import asyncio
import os
import json
import psycopg2
from nats.aio.client import Client as NATS
from src.llm_router import router

DB_DSN = os.getenv("DATABASE_URL", "postgresql://os_growth:os_growth_pass@nyota_db:5432/nyota_foundation")
NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")

SYSTEM_PROMPT = """You are Amani, the elite AI Content Writer for Nyota's Growth OS.
Your objective is to consume a target keyword and a scraped SEO context snippet, and draft a high-converting, SEO-optimized blog article.
Format the output in clean Markdown. Include an H1, H2s, and actionable paragraphs.
Keep the article tightly focused on the target keyword intent. Use a professional but engaging tone."""

def get_keyword_id(keyword: str):
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute("SELECT id FROM growth.keywords WHERE keyword = %s", (keyword,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"[Amani Error] DB Query failed: {e}")
        return None

def save_content_brief(keyword_id, title, content):
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO growth.content_briefs (keyword_id, title, markdown_content, status, created_at)
            VALUES (%s, %s, %s, 'DRAFTED', CURRENT_TIMESTAMP)
            RETURNING id
            """,
            (keyword_id, title, content)
        )
        brief_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return brief_id
    except Exception as e:
        print(f"[Amani Error] DB Insert failed: {e}")
        return None

async def run():
    nc = NATS()
    print("Amani (Growth AI Drafter) connecting to NATS...")
    while True:
        try:
            await nc.connect(NATS_URL)
            break
        except Exception as e:
            await asyncio.sleep(2)
            
    js = nc.jetstream()

    async def handle_drafting_job(msg):
        print(f"\n[EVENT] Amani intercepted: {msg.subject}")
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            keyword = payload.get("keyword", "")
            context = payload.get("context_snippet", "")
            
            if keyword:
                print(f"[Amani] Drafting SEO Post for '{keyword}'...")
                
                # We enforce Cloud for heavy drafting if context is massive, but Router handles it
                user_prompt = f"Target Keyword: {keyword}\n\nCompetitor Context from SERP:\n{context}\n\nPlease generate the full Markdown article now."
                
                # Offload to Intelligent LLM Router
                article_md = await router.generate_response(SYSTEM_PROMPT, user_prompt)
                
                print(f"[Amani] Completed draft. Size: {len(article_md)} chars.")
                
                # Persist to Postgres
                kw_id = get_keyword_id(keyword)
                if kw_id:
                    save_content_brief(kw_id, f"Ultimate Guide to {keyword.title()}", article_md)
                    print(f"[Amani] Saved draft to Postgres core.")
                    
                    # Fire completion event
                    finish_event = {
                        "domain": "growth",
                        "action": "content_drafted",
                        "payload": {
                            "keyword": keyword,
                            "length": len(article_md)
                        }
                    }
                    await js.publish("events.growth.content.drafted", json.dumps(finish_event).encode())
                else:
                    print(f"[Amani] Keyword ID not found. State may be out of sync.")
                
        except Exception as e:
            print(f"[Amani] Drafter failed: {e}")
            
        await msg.ack()

    # Amani listens to Zuri completing a crawl
    print("Amani is online and awaiting raw SEO context to process...")
    await js.subscribe("events.growth.crawler.completed", cb=handle_drafting_job)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
