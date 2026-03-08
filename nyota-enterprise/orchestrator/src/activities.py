from temporalio import activity
from nats.aio.client import Client as NATS
import json
import os

NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")

@activity.defn
async def trigger_growth_crawler(keyword: str) -> str:
    """
    Activity for publishing the trigger to Zuri to crawl.
    Since NATS is async and we need to wait for completion, ideally we would use 
    Temporal async-completion or HTTP to the Core API. For now, since Zuri doesn't 
    have a synchronous HTTP response, we trigger Zuri here, and rely on Temporal 
    signals to resume the workflow when Amani finishes writing.
    """
    activity.logger.info(f"Triggering Growth OS crawler for: {keyword}")
    
    nc = NATS()
    await nc.connect(NATS_URL)
    
    payload = {
        "action": "start",
        "target": "google_serp",
        "payload": {
            "target_keyword": keyword
        }
    }
    
    await nc.publish("events.growth.crawler.start", json.dumps(payload).encode())
    await nc.close()
    
    return "Crawler dispatched"

@activity.defn
async def verify_security_compliance(content_length: int) -> bool:
    """
    Mock activity simulating Baraka's verification of the drafted content.
    Returns True if safe.
    """
    activity.logger.info(f"Verifying security compliance of draft size: {content_length}")
    # Simulate DB lookup or Security OS call
    return True

@activity.defn
async def notify_human_approval(keyword: str) -> str:
    """
    Activity to send message to Telegram/Human for approval of article.
    """
    activity.logger.info(f"Notified human operator for approval of: {keyword}")
    return "Approval Requested"
