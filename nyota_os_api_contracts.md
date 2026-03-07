# Nyota v2 System Specification: OS API Contracts
## Synchronous Query & Debug Interfaces

### 1. Specification Overview
While the system is asynchronously driven by NATS, certain operations (Read-heavy UI, human debugging, immediate status checks) require synchronous API endpoints. Every Domain OS must expose a minimal internal API protected by Layer 4 security.

---

### 2. Authentication & Authorization
*   **Protocol:** mTLS for internal OS-to-OS calls.
*   **Auth Method:** Bearer Tokens issued by Nyota Core for Dashboard/Human access.
*   **Role-Based Access (RBAC):** 
    *   `viewer`: Read access only.
    *   `operator`: Can trigger non-destructive commands.
    *   `admin`: Full control (Core only).

---

### 3. API Catalog

#### 3.1 Growth OS (Port 8001)
*Manages traffic and visibility metrics.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/growth/keywords` | Current tracked keyword list with latest positions. |
| `GET` | `/growth/content/{id}` | Retrieve specific content item (draft or published). |
| `POST` | `/growth/content/publish` | Forces immediate publication of an approved draft. |
| `GET` | `/growth/crawler/status` | Real-time health of Playwright worker pool. |

**Request Schema (`/growth/content/publish`):**
```json
{
  "content_id": "uuid",
  "platforms": ["web", "postiz"],
  "schedule_immediate": true
}
```

---

#### 3.2 Revenue OS (Port 8002)
*Manages CRM and inventory state.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/revenue/inventory` | Real-time GPU stock and pricing. |
| `GET` | `/revenue/leads` | List of active leads in CRM pipeline. |
| `POST` | `/revenue/lead/assign` | Manually assign lead to Nia or human operator. |
| `GET` | `/revenue/stats` | Daily conversion rate and UGX revenue totals. |

**Request Schema (`/revenue/inventory`):**
```json
{
  "filter_category": "GPU",
  "min_margin": 15.0
}
```

---

#### 3.3 Infrastructure OS (Port 8003)
*Manages hardware and cloud deployments.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/infra/status` | Aggregated health of all nodes and containers. |
| `GET` | `/infra/terraform/state` | Current plan hash and resource count. |
| `POST` | `/infra/scale` | Request scaling of a specific service. (Security OS must validate). |
| `POST` | `/infra/rollback` | Immediate revert to previous versioned state. |

**Request Schema (`/infra/scale`):**
```json
{
  "service": "crawler",
  "replicas": 5,
  "rationale": "Sustained high load from GSC discovery"
}
```

---

#### 3.4 Security OS (Port 8004)
*Manages system integrity and intrusion logs.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/security/incidents` | Active threat detections or anomalies. |
| `GET` | `/security/audit` | Combined audit trail of command execution. |
| `POST` | `/security/quarantine` | Isolate specific IP, Service, or User. |
| `POST` | `/security/validate` | Endpoint for other OSs to check command safety. |

---

### 4. Rate Limiting & Performance

*   **Internal OS-to-OS:** Unlimited (1000req/sec burst).
*   **External Dashboard/Operator:** 60 requests per minute per IP.
*   **Timeout:** Default 30s. Long-running tasks (Crawl/Deploy) must return `202 Accepted` with a status URL.

### 5. Implementation Standard
*   **Format:** OpenAPI 3.0 (FastAPI Auto-docs).
*   **Encoding:** JSON (default), gRPC Protobuf for high-frequency Infra metrics.

