# Nyota v2 System Specification: Reference Architecture
## Full Enterprise Topology & Message Routing

### 1. Conceptual Topology Map
The Nyota v2 system separates business capabilities into bounded contexts (Operating Systems). No context has direct access to another's memory space.

```mermaid
graph TB
    subgraph "External World"
        WEB[Public Web / Google SERP]
        WAPP[Meta / WhatsApp API]
        GIT[GitHub / Production Code]
        DEV[Human Operator / DevOps]
    end

    subgraph "Nyota Core (Control Plane)"
        GW[API Gateway / Auth]
        ORC[Orchestrator Agent]
        DASH[Mission Control UI]
        DEV -->|mTLS / OAuth| GW
        GW --> DASH
        GW --> ORC
    end

    subgraph "The Nervous System"
        NATS(((NATS JetStream\nPersistent Event Bus)))
    end

    subgraph "OS Domains (Data Plane)"
        direction LR
        
        subgraph "Growth OS"
            G_SVC[Growth Services]
            G_AGT(Musa, Amani, Zuri)
            G_DB[(PG: Growth)]
            G_SVC <--> G_AGT
            G_SVC <--> G_DB
        end
        
        subgraph "Revenue OS"
            R_SVC[Revenue Services]
            R_AGT(Nia, GPU Sourcing)
            R_DB[(PG: Revenue_CRM)]
            R_CACHE[(Redis State)]
            R_SVC <--> R_AGT
            R_SVC <--> R_DB
            R_SVC <--> R_CACHE
        end
        
        subgraph "Security OS"
            S_SVC[Security Gate]
            S_AGT(Baraka Validator)
            S_LOG[(PG: Audit)]
            S_SVC <--> S_AGT
            S_SVC <--> S_LOG
        end
        
        subgraph "Infrastructure OS"
            I_SVC[Infra Commander]
            I_AGT(Jarvis SRE)
            I_TF[Terraform CLI]
            I_SVC <--> I_AGT
            I_AGT --> I_TF
        end
    end

    subgraph "Intelligence & Observability"
        TEMP{Temporal\nWorkflow Engine}
        QD[(Qdrant\nVector DB)]
        CH[(ClickHouse\nAnalytics)]
        LGTM[Loki, Grafana,\nTempo, Prometheus]
    end

    %% Routing
    WEB -->|Crawl| G_SVC
    WAPP <-->|Webhooks| R_SVC
    I_SVC -->|Deploy| GIT
    S_SVC -.->|Block/Allow| I_SVC
    
    %% Bus Connections
    GW <==> NATS
    G_SVC <==> NATS
    R_SVC <==> NATS
    I_SVC <==> NATS
    S_SVC <==> NATS
    
    %% Advanced connections
    NATS -.->|Triggers| TEMP
    NATS -.->|Metrics/Logs| LGTM
    G_SVC -.->|Embeddings| QD
    G_SVC -.->|Raw SERP| CH
```

---

### 2. Message Flow Diagram: The Complete Profit Loop
This diagram traces a standard user journey from Top-of-Funnel (Growth) to Bottom-of-Funnel (Revenue) and highlights how the distributed components handle the flow asynchronously.

```mermaid
sequenceDiagram
    participant User
    participant WhatsApp API
    participant Revenue OS (Nia)
    participant NATS Event Bus
    participant Growth OS (Postiz)
    participant Redis Cache (State)
    participant Postgres (CRM)

    User->>WhatsApp API: "How much for RTX 3060?"
    WhatsApp API->>Revenue OS (Nia): Webhook Payload
    
    Revenue OS (Nia)->>Redis Cache (State): Check Session Lock
    Redis Cache (State)-->>Revenue OS (Nia): Session Active (New Msg)
    
    Revenue OS (Nia)->>NATS Event Bus: Pub -> events.revenue.message.received
    
    note over Revenue OS (Nia), NATS Event Bus: Nia Agent calculates ROI & Inventory
    
    Revenue OS (Nia)->>NATS Event Bus: Pub -> events.revenue.price.quoted
    Revenue OS (Nia)->>Postgres (CRM): Insert Interaction Log
    Revenue OS (Nia)->>WhatsApp API: "1.3M UGX, available today."
    
    User->>WhatsApp API: "I will buy it."
    WhatsApp API->>Revenue OS (Nia): Webhook Payload
    
    Revenue OS (Nia)->>NATS Event Bus: Pub -> events.revenue.deal.closed
    Revenue OS (Nia)->>Postgres (CRM): Update Lead Status -> WON
    
    NATS Event Bus->>Growth OS (Postiz): Sub <- events.revenue.deal.closed
    note over Growth OS (Postiz): Cross-Domain Attribution
    Growth OS (Postiz)->>Growth OS (Postiz): Tally ROI for Traffic Source
    Growth OS (Postiz)->>NATS Event Bus: Pub -> events.growth.campaign.updated
```

---

### 3. Service Boundaries & Responsibilities Matrix

A strict matrix to enforce architectural discipline. If a new script or capability is developed, it must be assigned to one of these boundaries.

| OS Domain | Component Category | Permitted Actions | Blocked Actions |
| :--- | :--- | :--- | :--- |
| **Growth OS** | Crawlers, SEO Agents, Markdown Gens | Write to `growth` schema, Trigger PRs (via NATS), Ping Google APIs | Write to CRM, Access WhatsApp webhook, Alter Infrastructure |
| **Revenue OS** | Chatbots, Email Senders, Discount Engines | Write to `revenue` schema, Reply to WhatsApp, Read Inventory | Modify frontend code, Deploy servers, Scrape Google |
| **Security OS** | Intrusion Scanners, NGINX Configs, JWT Validation | Drop packets, Block incoming NATS events, Read audit logs | Write articles, Send emails to users |
| **Infrastructure OS** | Terraform, Docker Daemons, Cron | Provision VMs, Run GitHub Actions, Restart crashed containers | Read user chat logs, Modify marketing content |
| **Core (Orchestrator)** | API Gateway, Human Dashboard | Route mTLS traffic, Escalate alerts to Telegram, Issue mTLS certs | Run crawlers, Run Terraform, Run chat loops |

---

### 4. Advanced: Temporal Workflow Integration

For complex stateful logic spanning days (e.g., Cart Abandonment), the system relies on Temporal, which abstracts over the NATS bus.

```mermaid
graph LR
    subgraph "NATS Bus"
        EVENT(events.revenue.cart.abandoned)
    end
    
    subgraph "Temporal Engine"
        WF[Cart Recovery Workflow]
        TIMER(Wait 24 Hours)
        E_ACT(Execute Revenue OS Email API)
        C_ACT(Execute Growth OS Discount Ad)
        
        WF --> TIMER
        TIMER --> E_ACT
        TIMER --> C_ACT
    end
    
    EVENT -->|Start Workflow| WF
```

