# Nyota v2 System Specification: Event Schema
## Distributed Messaging Contract (NATS JetStream)

### 1. Specification Overview
This document defines the immutable event-driven contract for the Nyota v2 system. All inter-OS communication must adhere to these schemas. The system utilizes NATS JetStream for persistent message delivery, ensuring that even if an OS is offline, events are queued and delivered upon recovery.

---

### 2. Event Namespace Taxonomy
The namespace follows a strict hierarchy: `events.<domain>.<subdomain>.<action>`

| Domain | Scope |
| :--- | :--- |
| `events.growth` | Traffic generation, SEO, crawler results, content cycles. |
| `events.revenue` | CRM, lead conversion, inventory management, pricing. |
| `events.infrastructure` | Deployments, scaling, health metrics, IaC updates. |
| `events.security` | Threat detection, audit trails, execution gating. |
| `events.core` | High-level orchestration, human-in-the-loop approvals. |

---

### 3. Core Event Catalog

#### 3.1 Growth OS Events

| Event | Publisher | Subscribers | Action / Rationale |
| :--- | :--- | :--- | :--- |
| `events.growth.crawler.result` | Crawler (Zuri) | Musa, Baraka | New discovery found on competitor sites. |
| `events.growth.seo.brief_ready` | Musa | Amani, Core | Triggers content generation or strategy update. |
| `events.growth.content.drafted` | Amani | Core | Content is ready for human/orchestrator review. |
| `events.growth.content.published` | Growth OS | Revenue, Analytics | New URL live; notifies Revenue to update CTAs. |
| `events.growth.ranking.dropped` | Baraka | Musa, Core | Positions dropped > preset threshold. |

#### 3.2 Revenue OS Events

| Event | Publisher | Subscribers | Action / Rationale |
| :--- | :--- | :--- | :--- |
| `events.revenue.lead.captured` | Moltflow | Nia, Analytics | New WhatsApp/Form inquiry detected. |
| `events.revenue.deal.closed` | Nia | Growth, Analytics | Sale completed. Revenue OS records attribution. |
| `events.revenue.inventory.sold` | Inventory Agent | Growth, Postiz | GPU unit sold. Growth must update stock labels. |
| `events.revenue.price.adjusted` | Discount Engine | Growth, Postiz | Dynamic pricing changed based on ROI tracker. |
| `events.revenue.cart.abandoned` | Ecom Engine | Nia, Email | Trigger win-back sequence for identified users. |

#### 3.3 Infrastructure OS Events

| Event | Publisher | Subscribers | Action / Rationale |
| :--- | :--- | :--- | :--- |
| `events.infra.deploy.requested` | Jarvis | Security, Core | New Terraform/Code deploy proposed. |
| `events.infra.scale.triggered` | Jarvis | Security, Core | System scaling (up/down) initiated. |
| `events.infra.health.critical` | Monitor | Security, Core, Jarvis | Service down or OOM detected on production node. |
| `events.infra.backup.completed` | Backup Agent | Core, Security | Scheduled encrypted backup to S3 confirmed. |
| `events.infra.iac.drift_detected` | Jarvis | Security | Production state does not match Terraform local. |

#### 3.4 Security OS Events

| Event | Publisher | Subscribers | Action / Rationale |
| :--- | :--- | :--- | :--- |
| `events.security.threat.detected` | Baraka | Infra, Core | IPS/IDS trigger; immediate notification needed. |
| `events.security.exec.validated` | Baraka | Infra | Safe-exec.sh approved a command for execution. |
| `events.security.exec.blocked` | Baraka | Core | Malicious/Destructive command attempt captured. |
| `events.security.quarantine.active` | Security OS | Infra, Core | Target IP or Service is currently isolated. |
| `events.security.audit.anomaly` | Baraka | Core | Log analysis detected impossible travel or SSH brute-force. |

---

### 4. Payload Schemas (Standard Envelope)

Every NATS message must wrap its payload in a standard envelope.

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-03-07T10:48:39.000Z",
  "version": "2.0.0",
  "source": "os.growth.musa",
  "domain": "growth",
  "priority": "HIGH",
  "trace_id": "trace-uuid-v4",
  "payload": {}
}
```

#### Example 1: `events.revenue.inventory.sold`
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-07T10:50:00Z",
  "source": "os.revenue.inventory_tracker",
  "payload": {
    "item_sku": "GPU-RTX-3060-USED-LT1",
    "units_sold": 1,
    "remaining_stock": 7,
    "transaction_id": "TXN_UGX_1340000_123",
    "current_value_ugx": 1340000
  }
}
```

#### Example 2: `events.infra.deploy.requested`
```json
{
  "event_id": "771e9500-f38b-52e4-b827-557766551111",
  "source": "os.infra.jarvis",
  "payload": {
    "module": "terraform/aws/vpc",
    "change_set": "plan_file_binary_id",
    "risk_score": 7,
    "description": "Auto-scaling crawler nodes in secondary zone",
    "requires_security_validation": true
  }
}
```

---

### 5. Failure & Retry Behavior

All OS participants must implement the following JetStream policies:

1. **At-Least-Once Delivery:** Subscribers must send an `Ack` only after successful processing.
2. **Retry Intervals:** (Exponential Backoff) 5s, 30s, 5m, 1h.
3. **Dead Letter Queue (DLQ):** After 5 failed retries, events are moved to `dlq.events.error` for Baraka (Security) and Nyota Prime (Orchestrator) to analyze.
4. **Idempotency:** Subscribers must use `event_id` to prevent duplicate processing of the same signal.
5. **Flow Control:** If a subscriber is overwhelmed, it must signal NATS to slow down delivery using consumer flow control.

