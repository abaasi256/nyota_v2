# Nyota v2 System Changelog

All notable changes to the Nyota v2 Distributed Architecture will be documented in this file.

## [Unreleased]

### Phase 3 Started

- **Phase 3: Growth OS** implementation commenced.
- **Data Layer:** Initialized isolated `growth` schema in PostgreSQL with `growth.keywords` and `growth.content_briefs` tables.
- **Headless Crawler (`crawler_agent.py` - Zuri):** Built an autonomous asyncio Python HTTP crawler subscribing to `events.growth.crawler.start`, simulating Google SERP context extraction.
- **Content Writer (`amani_agent.py` - Amani):** Built an AI Drafter responding to crawler completion events, generating full markdown SEO posts via the LLM Router.
- Built explicit separation between the raw data extraction components and the intelligent modeling agents to allow independent container scaling.

### Phase 2 Complete

- **Phase 2: Revenue OS** implementation commenced.
- Built explicit separation between `nyota_revenue_api` (Moltflow Webhooks) and `nyota_revenue_nia` (Distributed AI worker).
- **Core Intelligence:** Created an Intelligent LLM Router (`llm_router.py`) implementing capability-based delegation prioritizing local, fast LLMs (Ollama) with fallback/escalation parsing to Cloud models (Kimi K2.5).
- **AI Worker (`nia_agent.py`):** Configured Nia to securely bind to the event bus, listen for WhatsApp messages (`events.revenue.lead.message`), and process semantic replies organically.
- Provisioned `/webhook/whatsapp` endpoint via FastAPI to ingest Moltflow callbacks.
- Created PostgreSQL `revenue.leads` schema to track CRM state.

## [2.1.0] - 2026-03-07

### Phase 1 Started

- **Phase 1: Sovereing Core** successfully deployed on Docker.
- `nyota_bus` (NATS JetStream) persistent event bus operational.
- `nyota_db` (Postgres 15) securely partitioned with `core`, `growth`, `revenue`, `infra`, and `security` schemas. Explicit RBAC enforced.
- `nyota_cache` (Redis 7.0) online.
- `nyota_core_gateway` decoupled API Gateway routing HTTP hits to NATS.
- `nyota_security_validator` (Baraka) active, auditing bus traffic and recording immutable logs to PostgreSQL.
