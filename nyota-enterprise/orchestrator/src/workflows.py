from temporalio import workflow
from datetime import timedelta
import asyncio

with workflow.unsafe.imports_passed_through():
    from src.activities import (
        trigger_growth_crawler,
        verify_security_compliance,
        notify_human_approval,
    )

@workflow.defn
class ContentGenerationWorkflow:
    def __init__(self) -> None:
        self.draft_completed = False
        self.draft_length = 0
        self.human_approved = False

    @workflow.signal
    async def amani_completion_signal(self, content_length: int) -> None:
        self.draft_completed = True
        self.draft_length = content_length

    @workflow.signal
    async def trigger_human_approval(self) -> None:
        self.human_approved = True

    @workflow.run
    async def run(self, keyword: str) -> str:
        # Step 1: Trigger Research & Crawling
        await workflow.execute_activity(
            trigger_growth_crawler,
            keyword,
            start_to_close_timeout=timedelta(seconds=60),
        )

        # Step 2: Wait for Drafting Completion Signal (Amani finishes writing)
        await workflow.wait_condition(
            lambda: self.draft_completed,
            timeout=timedelta(minutes=30)
        )

        if not self.draft_completed:
            return "Failed to receive drafted content in time."

        # Step 3: Verification (Baraka Security Check)
        is_safe = await workflow.execute_activity(
            verify_security_compliance,
            self.draft_length,
            start_to_close_timeout=timedelta(seconds=30),
        )

        if not is_safe:
            return "Security check failed. Content quarantined."

        # Step 4: Approval Gate
        await workflow.execute_activity(
            notify_human_approval,
            keyword,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Step 5: Await manual Telegram approval via Workflow Signal
        await workflow.wait_condition(
            lambda: self.human_approved,
            timeout=timedelta(hours=24)
        )
        
        if not self.human_approved:
            return "Human approval timeout."

        return f"Content Generation for '{keyword}' Approved & Published Successfully."
