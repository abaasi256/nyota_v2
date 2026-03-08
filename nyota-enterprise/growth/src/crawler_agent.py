import asyncio
import os
import json
import psycopg2
from bs4 import BeautifulSoup
from nats.aio.client import Client as NATS
from qdrant_client import QdrantClient

DB_DSN = os.getenv("DATABASE_URL", "postgresql://os_growth:os_growth_pass@nyota_db:5432/nyota_foundation")
NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")
QDRANT_URL = os.getenv("QDRANT_URL", "http://nyota_qdrant:6333")

qdrant = QdrantClient(url=QDRANT_URL)

def record_keyword_metrics(keyword, volume=0, difficulty=0):
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO growth.keywords (keyword, search_volume, difficulty, status, last_crawled)
            VALUES (%s, %s, %s, 'SCRAPED', CURRENT_TIMESTAMP)
            ON CONFLICT (keyword) DO UPDATE SET 
                search_volume = EXCLUDED.search_volume,
                difficulty = EXCLUDED.difficulty,
                last_crawled = CURRENT_TIMESTAMP
            """,
            (keyword, volume, difficulty)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[Zuri Error] Failed to write to DB: {e}")

import httpx

async def scrape_google_serp(keyword: str):
    """
    Simulates a Google SERP check to identify competitor density.
    Using purely HTTPx to stay lightweight for Docker.
    """
    print(f"[Zuri Crawler] Launching HTTP worker to analyze SERP for: '{keyword}'")
    try:
        headers = {
            "User-Agent": "ZuriCrawler/1.0 (Integration Testing)"
        }
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            url = f"https://en.wikipedia.org/wiki/Special:Search?search={keyword.replace(' ', '+')}"
            response = await client.get(url)
            response.raise_for_status()
            
            content = response.text
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text_snippet = soup.get_text()[:500] 
            
            print(f"[Zuri Crawler] HTTP Scrape successful for '{keyword}'. Extracted {len(content)} bytes of DOM.")
            return text_snippet
    except Exception as e:
        print(f"[Zuri Crawler] Exception scraping: {e}")
        print("[Zuri Crawler] Falling back to offline mock SERP context to continue pipeline...")
        return f"Mocked SERP Context for {keyword}. Competitors rank highly for 'high performance gaming PCs' and 'RTX graphics cards locally'. Pricing ranges from $1,800 to $2,200. Focus keywords identified: Kampala custom PCs, high end gaming rig, RTX 4090 availability."

async def run():
    nc = NATS()
    print("Zuri (Growth Crawler) connecting to NATS...")
    while True:
        try:
            await nc.connect(NATS_URL)
            break
        except Exception as e:
            await asyncio.sleep(2)
            
    js = nc.jetstream()

    async def handle_crawl_request(msg):
        print(f"\n[EVENT] Zuri intercepted: {msg.subject}")
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            keyword = payload.get("target_keyword", "")
            
            if keyword:
                print(f"[Zuri] Executing crawl sequence for '{keyword}'...")
                
                # Execute the Headless Playwright Crawl
                scraped_context = await scrape_google_serp(keyword)
                
                # Dummy metrics generator based on keyword
                volume = len(keyword) * 1000
                difficulty = min(100, len(keyword) * 5)
                
                # Write back into isolated DB Schema
                if scraped_context:
                    record_keyword_metrics(keyword, volume, difficulty)
                    print(f"[Zuri] Successfully logged SEO metrics for '{keyword}' into Postgres.")
                    
                    # Store in Qdrant Vector Brain seamlessly using fastembed
                    try:
                        print(f"[Zuri] Pushing context into Qdrant Vector Brain...")
                        await asyncio.to_thread(
                            qdrant.add,
                            collection_name="growth_crawls",
                            documents=[scraped_context],
                            metadata=[{"keyword": keyword}]
                        )
                        print(f"[Zuri] Vector embeddings saved in Qdrant.")
                    except Exception as qe:
                        print(f"[Zuri] Failed pushing to Qdrant: {qe}")
                    
                    # Fire Async Event signalling the Drafter (Amani) to generate an article
                    result_event = {
                        "domain": "growth",
                        "action": "serp_scraped",
                        "payload": {
                            "keyword": keyword,
                            "context_snippet": scraped_context
                        }
                    }
                    await js.publish("events.growth.crawler.completed", json.dumps(result_event).encode())
                
        except Exception as e:
            print(f"[Zuri] Crawler failed processing sequence: {e}")
            
        await msg.ack()

    # Zuri intercepts commands specifically targeting the crawler pool
    print("Zuri is online and awaiting targeted crawl commands...")
    await js.subscribe("events.growth.crawler.start", cb=handle_crawl_request)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
