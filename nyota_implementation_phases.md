# Nyota v2 Implementation Plan
## Phased Distributed Rollout Strategy

To transition from zero to a fully distributed autonomous enterprise, the implementation of Nyota v2 is strictly phased. Attempting a "Big Bang" deployment of all four Operating Systems simultaneously guarantees failure. We build the spine, then attach the operational limbs, and finally enable the advanced cognitive memory and tracing.

---

## Phase 1 — The Sovereign Core (M1)
**Objective:** Establish the immutable event bus, internal persistence, and the zero-trust security gateway. This phase proves the communication architecture works.

*   **System Components:**
    *   **NATS JetStream:** The central event bus.
    *   **PostgreSQL:** The primary relational data store (shared cluster, logically separated schemas).
    *   **Redis:** Working memory and rate-limiting cache.
    *   **Nyota Core (Orchestrator):** API Gateway and human-approval escalation loop.
    *   **Security OS (Baraka):** Payload validator and execution gatekeeper.
*   **Deployment Dependencies:** Docker Swarm / Compose foundation, valid mTLS certificates for inter-service auth.
*   **Infrastructure Requirements:** 
    *   Compute: 2 vCPU, 4GB RAM minimum (Control Plane Node).
    *   Storage: 50GB NVMe (NATS JetStream persistence, Postgres WAL).
*   **Engineering Complexity:** **Medium**. This is standard distributed systems plumbing.
*   **Success Criteria:** Nyota Core can publish an event (`events.core.ping`), NATS persists it, and the Security OS consumes and logs it to PostgreSQL.
*   **Failure Risks:** Misconfigured JetStream replication causing message loss on restart; overly restrictive Postgres RBAC preventing schema initialization.

---

## Phase 2 — The Revenue OS (M2)
**Objective:** Monetize the platform. Bring the existing e-commerce and WhatsApp logic into the event-driven fold before scaling traffic.

*   **System Components:**
    *   **Moltflow Integration:** WhatsApp webhook receiver publishing to NATS.
    *   **CRM Engine:** Postgres-backed lead state management.
    *   **Sales Agent (Nia v2):** Conversational AI processor.
    *   **Inventory Manager:** Tracks the $10M UGX physical GPU stock.
*   **Deployment Dependencies:** Phase 1 Core functional. Approved Meta/WhatsApp Business API webhooks pointing to the Nyota Core API Gateway.
*   **Infrastructure Requirements:**
    *   Compute: +1 vCPU, 2GB RAM.
*   **Engineering Complexity:** **High**. Handling asynchronous, human-in-the-loop chat state over NATS requires robust deduplication and idempotency logic.
*   **Success Criteria:** A user sends a WhatsApp message -> Core authenticates -> Moltflow transforms to `events.revenue.lead.message` -> Nia generates response -> System updates Postgres CRM and replies to user successfully.
*   **Failure Risks:** Meta API rate limits blocking outbound messages; concurrent updates to inventory leading to overselling race conditions.

---

## Phase 3 — The Growth OS (M3)
**Objective:** Automate traffic generation and content velocity now that the business can convert leads.

*   **System Components:**
    *   **Crawler Cluster (Zuri):** Headless Playwright workers scraping SERPs.
    *   **SEO Strategist (Musa v2):** Keyword gap analysis logic.
    *   **Content Generator (Amani v2):** LLM prompt chaining and markdown generation.
    *   **Omnichannel Publisher:** Integration with `company-skills/postiz`.
*   **Deployment Dependencies:** Phase 1 Core. Third-party scraping proxy IPs. Anthropic/OpenAI API access.
*   **Infrastructure Requirements:**
    *   Compute: +4 vCPU, 8GB RAM (Playwright browsers are compute and memory intensive).
*   **Engineering Complexity:** **Very High**. Managing headless browser zombie processes and controlling LLM context windows to prevent token exhaustion.
*   **Success Criteria:** Musa identifies a keyword gap, Amani drafts a 1000-word article, Security OS approves the markdown, and it is published to the live site via Git Gateway.
*   **Failure Risks:** Cloudflare/CAPTCHA blocks stopping crawlers; LLM hallucinating fake product specs; run-away API costs from infinite generation loops.

---

## Phase 4 — Advanced Systems & Intelligence (M4)
**Objective:** Elevate the system from a "smart automation script" to a true enterprise autonomous entity with long-term memory, observability, and indestructible workflows.

*   **System Components:**
    *   **Temporal Server:** Stateful workflow orchestration replacing simple async queues.
    *   **ClickHouse:** High-volume analytics ingestion for crawler logs and telemetry.
    *   **Qdrant:** Vector database for semantic search across past articles and competitor data.
    *   **LGTM Stack:** Loki, Grafana, Tempo, Prometheus for full stack observability.
*   **Deployment Dependencies:** Phases 1-3 fully operational and stable.
*   **Infrastructure Requirements:**
    *   Compute: +8 vCPU, 16GB RAM.
    *   Storage: +200GB SSD for log aggregation and ClickHouse columnar storage.
*   **Engineering Complexity:** **Extreme**. Integrating OpenTelemetry traces across asynchronous NATS queues and Temporal workflows is highly complex.
*   **Success Criteria:** You can query Qdrant for "articles similar to X", view a complete distributed trace of a user's journey from Page View to WhatsApp Sale in Grafana Tempo, and Temporal automatically recovers a failed deployment workflow.
*   **Failure Risks:** OOM (Out of Memory) crashes on ClickHouse or Qdrant due to improper JVM/heap sizing; tracing context headers dropping at the NATS boundary.

