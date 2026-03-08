# Nyota OS v2: Enterprise Deployment Guide 🚀

This document provides the standard operating procedures (SOPs) for provisioning, deploying, and scaling the Nyota v2 Multi-Agent Swarm. It covers both local development environments and production-grade deployments.

---

## 🏗️ Deployment Architecture

Nyota v2 operates as a sovereign, decoupled microservice architecture. It strictly utilizes a **"Shared-Nothing"** pattern among AI agents, relying entirely on an immutable event bus (NATS) and a stateful Saga orchestrator (Temporal).

The cluster is composed of **12 distinct containers**:

1.  **State & Memory Layer (Volumes Required)**
    *   `nyota_bus` (NATS JetStream): Persistent event streaming.
    *   `nyota_db` (Postgres 15): Multi-schema relational state.
    *   `nyota_cache` (Redis 7): Sub-millisecond rate-limiting and working memory.
    *   `nyota_qdrant` (Qdrant): Vector database for Agent RAG (Long-Term Memory).
    *   `nyota_temporal` (Temporal): Workflow execution persistence.

2.  **API Gateways (Exposed Ports)**
    *   `nyota_core_gateway` (FastAPI - Port 8000): Ingress and WebSockets.
    *   `nyota_revenue_api` (FastAPI - Port 8001): Webhook ingress for CRM.

3.  **Autonomous Workers (Internal Network Only)**
    *   `nyota_growth_zuri`: Headless Playwright crawler.
    *   `nyota_growth_amani`: AI Drafter utilizing Qdrant memory.
    *   `nyota_revenue_nia`: Conversational AI Sales Engineer.
    *   `nyota_security_validator` (Baraka): Zero-trust network auditor.
    *   `nyota_orchestrator`: Temporal worker mapping NATS events to Sagas.

4.  **Presentation Layer**
    *   `nyota_dashboard` (Nginx/React - Port 3000): Mission Control UI.

---

## 🖥️ Local & Staging Deployment (Docker Compose)

The fundamental requirement for running Nyota v2 locally is a minimum of **8GB RAM** allocated to the Docker Engine. The headless Playwright node (`Zuri`) and the local LLMs (if utilizing Ollama) demand substantial compute.

### 1. Environment Preparation
Ensure your `.env.core` file is populated securely at the root of `nyota-enterprise`:

```env
NYOTA_ENV=production
NYOTA_DB_ADMIN=nyota_admin
NYOTA_DB_PASSWORD=secure_dev_password
OLLAMA_BASE_URL=http://host.docker.internal:11434
KIMI_API_KEY=your_production_key_here
```

### 2. Swarm Initialization
Execute the following to build the optimized production images (utilizing Docker BuildKit):

```bash
docker compose build --no-cache
docker compose up -d
```

### 3. Verification Sequence
Confirm the cluster health via the diagnostic layers:
*   **Mission Control:** `http://localhost:3000`
*   **Temporal Web UI:** `http://localhost:8080`
*   **NATS JetStream Monitor:** `http://localhost:8222`

---

## 🌍 Production Deployment Strategies

When transitioning to a production environment (such as AWS, GCP, or a bare-metal swarm), you must migrate from Docker Compose networks to a highly available orchestrator.

### Strategy 1: Kubernetes (K8s) Cluster
**Recommended for: High-traffic SaaS environments scaling beyond thousands of leads per day.**

1.  **Persistent Volumes:** You *must* map `nats_data`, `pg_data`, and `qdrant_data` to managed storage (e.g., AWS EBS) using PersistentVolumeClaims (PVCs). Do not rely on ephemeral container storage.
2.  **StatefulSets vs Deployments:**
    *   Deploy `nyota_bus` (NATS), `nyota_db`, `nyota_qdrant` as **StatefulSets**.
    *   Deploy all AI Agents (Zuri, Amani, Nia) as **Deployments** connected to a Horizontal Pod Autoscaler (HPA).
3.  **Autoscaling Metrics:** Configure the HPA to scale `nyota_growth_amani` based on NATS queue depth, *not* CPU utilization. If the `events.growth.crawler.completed` stream backs up, K8s should spawn more Amani nodes to handle the drafting load.

### Strategy 2: Distributed Edge Nodes
**Recommended for: Maximizing Local LLM Performance & Cost Reduction.**

1.  Separate the components physically. Run the Core Infrastructure (Postgres, NATS, APIs) on a standard Cloud VM (e.g., DigitalOcean).
2.  Deploy the AI Agents (Amani, Nia) directly onto **on-premise workstations equipped with high-end GPUs (e.g., RTX 4090s)** running Ollama.
3.  Connect the edge workers back to the Cloud NATS bus via TLS over internet. Because agents communicate entirely via event streams, latency across the WAN is perfectly handled by NATS, allowing you to bypass tremendous cloud GPU costs.

---

## 🛡️ Pre-Flight Security Checklist

Before exposing the Gateways publicly:
1.  **Nginx Reverse Proxy:** Never expose port 8000 (FastAPI) or 3000 (React) directly to the WAN. Reverse proxy them behind Nginx or Traefik with automatic SSL provisioning (Let's Encrypt).
2.  **API Rate Limiting:** Enforce strict Redis-backed limits on `/api/revenue/whatsapp` to prevent SMS/CRM bombing.
3.  **Network Isolation:** Ensure `nyota_core_net` does not export ports for internal agents. External traffic should strictly terminate at the FastAPI gateways.

> *Documented by: Autonomus Deepmind Cell (Architect)*
