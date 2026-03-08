# Nyota OS v2 🪐

Nyota v2 is an elite, **multi-agent distributed autonomous platform** designed to operate as a completely autonomous digital enterprise. Built upon a sovereign architecture of event-driven microservices, it orchestrates intelligent AI agents using a Saga pattern to autonomously handle revenue generation, content creation, infrastructure scaling, and security auditing.

*"Where static automation ends, autonomous operations begin."*

---

## 🏗️ Architecture Overview

The system is partitioned into **Four Specialized Operating Systems**, bridged together by an immutable event bus and a stateful workflow orchestrator.

1. **Nyota Core (The Foundation)**
   - **Nervous System:** NATS JetStream (`nyota_bus`) for zero-latency, decoupled, persistent event communication.
   - **Memory:** PostgreSQL 15 (`nyota_db`) utilizing multi-tenant schemas (`core`, `growth`, `revenue`, `infra`, `security`) secured via RBAC.
   - **Cache:** Redis 7.0 (`nyota_cache`) for rate-limiting and working memory.
   - **Gateway:** FastAPI (`core_api`) bridges inbound HTTP traffic and WebSockets directly to the NATS bus.

2. **Growth OS (The Traffic Engine)**
   - **Zuri (Crawler):** A headless, asynchronous HTTP worker capable of executing deep SERP extractions to discover keyword gaps and competitor contexts.
   - **Amani (Drafter):** A generative AI agent that intercepts Zuri's data and drafts highly optimized, long-form SEO Markdown articles.

3. **Revenue OS (The Profit Loop)**
   - **Nia (Sales Engineer):** An AI worker natively synced with a Postgres CRM, directly analyzing intent scores and automating conversational sales (i.e., quoting hardware/GPU pricing) over WhatsApp.
   - **Webhook Gateway:** Natively binds to SaaS webhook callbacks (e.g., Moltflow).

4. **Security & Infra OS (The Shield & Muscle)**
   - **Baraka (Validator):** An immutable zero-trust gatekeeper that audits every NATS payload and persists an unalterable ledger.
   - **Mission Control UI:** A React/Vite Glassmorphism dashboard providing live telemetry, WS streams, and dynamic data polling.
   - **Temporal Orchestrator:** Stateful Saga coordinator to manage retries, wait states, and human-in-the-loop approvals across disparate agents.

---

## 🚦 Quick Start Guide

### 1. Prerequisites
- **Docker & Docker Compose** (Ensure Docker Desktop is allocated at least 8GB RAM).
- **Git** (to clone the repository).
- **Ollama** installed locally (running on `host.docker.internal:11434` for local AI executions).

### 2. Startup Swarm
Initialize the entire ecosystem with a single command:

```bash
docker compose up -d --build
```

### 3. Verify Health
All 11 enterprise containers will spin up. Access the critical diagnostic tools:
- **Mission Control Dashboard:** http://localhost:3000
- **Temporal Workflow UI:** http://localhost:8080
- **NATS JetStream Monitor:** http://localhost:8222

---

## 🔐 Environments & Configuration

The cluster expects an environment file at `nyota-enterprise/.env.core` to properly map database credentials and intelligent API fallbacks.

```env
# nyota-enterprise/.env.core
NYOTA_ENV=production
NYOTA_DB_ADMIN=nyota_admin
NYOTA_DB_PASSWORD=secure_dev_password

# LLM Routing Configuration (Intelligent Model Fallback)
# Priority 1: High-Speed Local Open-Source AI
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# Priority 2: Cloud AI Fallback for Complex Logic (Escalation)
KIMI_API_KEY=your_kimi_api_key_here
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k
```

---

## 🔌 Channel Connections & Webhooks

### Telegram (Human-in-the-loop Approvals)
Workflows configured in `nyota_orchestrator` can suspend execution state using Temporal's SDK to await a human signal. 
*Example:* Amani generates an article -> The Orchestrator halts -> Pings a Telegram Bot API with a preview link -> Awaits a `/approve` webhook signal to resume publishing.

### WhatsApp (Moltflow CRM)
The Revenue OS API provides an open `/webhook/whatsapp` ingress.
1. Connect your Meta Business API / Moltflow account to `https://<YOUR-NGROK_TUNNEL>/webhook/whatsapp`.
2. When a lead texts your number, the webhook fires.
3. The Revenue API translates this to an `events.revenue.lead.message` NATS packet.
4. **Nia** (AI Agent) intercepts, calculates intent, queries the DB for pricing, and executes the exact outbound Meta API response autonomously.

---

## ⚡ Workflows & Execution Design

Nyota v2 runs on a stateful **Saga Architecture** coordinated by Temporal. Micro-agents operate purely on decoupled events without waiting for one another, whilst the Orchestrator tracks the macro-process.

### Example: Content Generation Pipeline (Triggered natively via NATS)
```bash
# Simulating a human triggering a workflow from Mission Control:
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/bus/publish/orchestrator/start_workflow" `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"action":"start","target":"system","data":{"target_keyword":"AI automation trends"}}'
```

1. **Temporal Execution Started:** The orchestrator binds the `ContentGenerationWorkflow` timeline.
2. **Activity 1 (Zuri):** Orchestrator commands the crawler to scrape the SERP context.
3. *Asynchronous Wait:* Temporal sleeps the workflow without locking threads until a NATS JetStream signal confirms completion.
4. **Event Fired:** Amani detects Zuri's context, writes the article, stores it in Postgres, and fires `events.growth.content.drafted`.
5. **Workflow Resumed:** Orchestrator intercepts Amani's signal, injects it back into Temporal.
6. **Activity 2 (Human Approval):** Trigger a Telegram alert to an admin. Workflow suspends.
7. **Publish:** Over Git Gateway once manually approved.

---

## 🧠 Usecase Examples

**1. Scalable SEO Dominance:**
You upload a CSV of 1,000 keywords to the Core API. Growth OS disperses this across multiple Zuri node containers. As contexts stream back, 5 Amani node containers generate thousands of words of high-quality Markdown SEO content, all monitored safely by Baraka and held in Postgres until Human Approval. 

**2. Intelligent Hardware Sales:**
A user texts your commercial WhatsApp asking *"Do you have the RTX 4090 in stock in Kampala?"*. The Revenue OS immediately searches the Postgres `revenue` schemas. Nia detects the high-purchase intent, responds *"Yes, we have 3 units remaining at $2,100"*, updates the pipeline forecast, and flags the deal on your Mission Control Dashboard.

**3. Infrastructure Self-Healing:**
If the NATS bus throughput detects an anomalous DDoS spike, the Security OS intercepts the audit log, fires an `events.security.threat.detected` event. A Temporal orchestrator halts all non-critical crawling operations immediately to preserve compute overhead for the active CRM traffic, protecting revenue at the expense of automated marketing.

---

## 🛠️ Tech Stack
* **Languages:** Python (AI/Data), TypeScript (React/UI)
* **Brokers:** NATS JetStream, Temporal.io
* **Compute:** Docker Compose, Nginx, FastAPI
* **Data:** PostgreSQL 15, Redis 7
* **Frontend:** Vite, React, Framer Motion, Recharts
* **LLMs:** Ollama, Kimi K2.5 (OpenAI-Compatible routing)

> *Authored by the Autonomus Deepmind Cell.*
