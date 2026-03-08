import asyncio
import os
import json
import logging
from temporalio.client import Client as TemporalClient
from temporalio.worker import Worker
from nats.aio.client import Client as NATS

from src.activities import (
    trigger_growth_crawler,
    verify_security_compliance,
    notify_human_approval,
)
from src.workflows import ContentGenerationWorkflow

NATS_URL = os.getenv("NATS_URL", "nats://nyota_bus:4222")
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "nyota_temporal:7233")

logging.basicConfig(level=logging.INFO)

async def start_worker():
    logging.info(f"Connecting to Temporal cluster at {TEMPORAL_HOST}...")
    
    # Retry connecting to Temporal cluster (as it might be starting up in Docker Compose)
    for _ in range(10):
        try:
            temporal_client = await TemporalClient.connect(TEMPORAL_HOST, namespace="default")
            break
        except Exception:
            await asyncio.sleep(5)
    else:
        raise Exception("Failed to connect to Temporal Server after retries.")
        
    logging.info("Connected to Temporal. Starting Worker...")

    worker = Worker(
        temporal_client,
        task_queue="growth-task-queue",
        workflows=[ContentGenerationWorkflow],
        activities=[
            trigger_growth_crawler,
            verify_security_compliance,
            notify_human_approval,
        ],
    )
    
    # We run the worker as a background task
    return temporal_client, worker, asyncio.create_task(worker.run())

async def run_nats_listener(temporal_client):
    nc = NATS()
    logging.info(f"Orchestrator connecting to NATS at {NATS_URL}...")
    while True:
        try:
            await nc.connect(NATS_URL)
            break
        except Exception:
            await asyncio.sleep(2)
            
    js = nc.jetstream()
    
    # 1. Listener for initiating the workflow
    async def start_content_workflow(msg):
        logging.info("Received request to start ContentGenerationWorkflow via NATS.")
        try:
            data = json.loads(msg.data.decode())
            keyword = data.get("payload", {}).get("target_keyword", "")
            if keyword:
                workflow_id = f"content-gen-{keyword.replace(' ', '-')}"
                await temporal_client.start_workflow(
                    ContentGenerationWorkflow.run,
                    keyword,
                    id=workflow_id,
                    task_queue="growth-task-queue",
                )
                logging.info(f"Started Temporal Workflow: {workflow_id}")
        except Exception as e:
            logging.error(f"Failed to start workflow: {e}")
        await msg.ack()

    # 2. Listener for completing Amani Draft
    async def signal_draft_completion(msg):
        logging.info("Amani drafted content. Signaling Workflow...")
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            keyword = payload.get("keyword", "")
            length = payload.get("length", 0)
            
            workflow_id = f"content-gen-{keyword.replace(' ', '-')}"
            handle = temporal_client.get_workflow_handle(workflow_id)
            
            await handle.signal(ContentGenerationWorkflow.amani_completion_signal, length)
            logging.info(f"Signaled Amani completion to {workflow_id}")
        except Exception as e:
            logging.error(f"Failed to signal workflow: {e}")
        await msg.ack()

    await js.subscribe("events.orchestrator.start_workflow.>", cb=start_content_workflow)
    await js.subscribe("events.growth.content.drafted", cb=signal_draft_completion)
    
    logging.info("Orchestrator NATS Listeners online.")

async def main():
    try:
        temporal_client, worker, worker_task = await start_worker()
        await run_nats_listener(temporal_client)
        # Keep process alive
        await asyncio.Event().wait()
    except Exception as e:
        logging.getLogger(__name__).error(f"Orchestrator Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
