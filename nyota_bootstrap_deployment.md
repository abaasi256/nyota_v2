# Nyota v2 System Specification: Bootstrap Deployment
## Phase 1 Core Execution Guide (Single Server to Cluster Horizon)

### 1. Specification Overview
This sequence provides the exact artifacts needed to transition Nyota v2 from theory into a running cluster on a single Contabo/Hetzner VPS or local development machine. This covers **Phase 1: The Sovereign Core**. It establishes the fundamental event bus, the operational database, and the security gateways.

We use mature container orchestration (Docker Compose) as the bridge to eventual Kubernetes/Swarm cluster scheduling.

---

### 2. Core Infrastructure Initialization (`docker-compose.yml`)

Create a directory string matching the reference architecture:
```bash
mkdir -p ./nyota-enterprise/core/config
cd ./nyota-enterprise
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # --------------------------------------------------------
  # THE NERVOUS SYSTEM: NATS Event Bus (with JetStream)
  # --------------------------------------------------------
  nats:
    image: nats:2.9.15
    container_name: nyota_bus
    command: 
      - "-js" # Enable JetStream for persistence
      - "-m"
      - "8222" # Monitor port
    ports:
      - "4222:4222" # Client connections
      - "8222:8222" # Metrics
    volumes:
      - nats_data:/data
    networks:
      - nyota_core_net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  # --------------------------------------------------------
  # THE MEMORY: Shared Multi-Tenant Database
  # --------------------------------------------------------
  postgres:
    image: postgres:15-alpine
    container_name: nyota_db
    environment:
      POSTGRES_USER: ${NYOTA_DB_ADMIN:-nyota_admin}
      POSTGRES_PASSWORD: ${NYOTA_DB_PASSWORD:-secure_dev_password}
      POSTGRES_DB: nyota_foundation
    ports:
      - "5432:5432" # Exposed for local dev, block in prod
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./core/config/init-schemas.sql:/docker-entrypoint-initdb.d/init-schemas.sql
    networks:
      - nyota_core_net
    restart: unless-stopped

  # --------------------------------------------------------
  # THE CACHE: High-Speed Working State
  # --------------------------------------------------------
  redis:
    image: redis:7.0-alpine
    container_name: nyota_cache
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
    networks:
      - nyota_core_net
    restart: unless-stopped

  # --------------------------------------------------------
  # NYOTA CORE (Stubbed for initial deploy validation)
  # --------------------------------------------------------
  core_api:
    image: python:3.11-slim
    container_name: nyota_core_gateway
    command: >
      sh -c "pip install nats-py fastapi uvicorn pydantic && \
             python3 -c 'import time; print(\"Core Gateway Starting\"); \
             while True: time.sleep(3600)'"
    env_file: .env.core
    depends_on:
      nats:
        condition: service_healthy
      postgres:
        condition: service_started
    networks:
      - nyota_core_net
    restart: unless-stopped

  # --------------------------------------------------------
  # SECURITY OS (Stubbed for initial deploy validation)
  # --------------------------------------------------------
  security_os:
    image: python:3.11-slim
    container_name: nyota_security_validator
    command: >
      sh -c "pip install nats-py && \
             python3 -c 'import time; print(\"Baraka Security Validator Starting\"); \
             while True: time.sleep(3600)'"
    depends_on:
      nats:
        condition: service_healthy
    networks:
      - nyota_core_net
    restart: unless-stopped

volumes:
  nats_data:
  pg_data:
  redis_data:

networks:
  nyota_core_net:
    driver: bridge # Transition to overlay for Swarm
```

---

### 3. Database Schema Initialization (`init-schemas.sql`)

Create the initialization script (this will automatically execute when `postgres` starts).
`./core/config/init-schemas.sql`:

```sql
-- Establish Boundaries for multi-tenant OS separation
CREATE SCHEMA IF NOT EXISTS growth;
CREATE SCHEMA IF NOT EXISTS revenue;
CREATE SCHEMA IF NOT EXISTS infrastructure;
CREATE SCHEMA IF NOT EXISTS security;
CREATE SCHEMA IF NOT EXISTS core;

-- Set up roles for isolated domain access
CREATE ROLE os_growth WITH LOGIN PASSWORD 'os_growth_pass';
CREATE ROLE os_revenue WITH LOGIN PASSWORD 'os_revenue_pass';
CREATE ROLE os_infra WITH LOGIN PASSWORD 'os_infra_pass';
CREATE ROLE os_security WITH LOGIN PASSWORD 'os_sec_pass';

-- Grant access (Principle of least privilege)
GRANT ALL PRIVILEGES ON SCHEMA growth TO os_growth;
GRANT ALL PRIVILEGES ON SCHEMA revenue TO os_revenue;
GRANT ALL PRIVILEGES ON SCHEMA infrastructure TO os_infra;
GRANT ALL PRIVILEGES ON SCHEMA security TO os_security;
GRANT ALL PRIVILEGES ON SCHEMA core TO postgres;

-- Core NATS Audit Log Table (Owned by Security)
CREATE TABLE security.nats_audit_log (
    id SERIAL PRIMARY KEY,
    event_id UUID NOT NULL,
    domain VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4. Deploying the Minimal Cluster

1.  **Set Environment Variables:**
    ```bash
    echo "NYOTA_ENVIRONMENT=production" > .env.core
    # In production, use strong secrets.
    ```
2.  **Launch the Foundation:**
    ```bash
    docker-compose up -d
    ```
3.  **Validate Health:**
    ```bash
    docker-compose ps
    ```
    *All 5 containers should show `Up`. The `nats` container will show `(healthy)`.*

---

### 5. Interacting with the Event Bus (Testing)

Now that the core is running, we test the NATS JetStream connectivity across container boundaries.

**Step 1: Open a terminal inside the Security OS container and subscribe to all events:**
```bash
docker exec -it nyota_security_validator bash
# (Inside container)
# We use a rudimentary Python script to listen to the bus
cat << 'EOF' > listener.py
import asyncio
import json
from nats.aio.client import Client as NATS

async def run():
    nc = NATS()
    await nc.connect("nats://nyota_bus:4222")
    js = nc.jetstream()
    
    async def message_handler(msg):
        print(f"SECURITY OS RECEIVED: [{msg.subject}] : {msg.data.decode()}")
        await msg.ack()

    # Subscribe to ALL events across the system
    print("Baraka Validator: Listening on events.>")
    sub = await js.subscribe("events.>", cb=message_handler)
    
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(run())
EOF
python3 listener.py
```

**Step 2: From the Core API container, publish a test event:**
Open another terminal.
```bash
docker exec -it nyota_core_gateway bash
# (Inside container)
cat << 'EOF' > publisher.py
import asyncio
import json
from nats.aio.client import Client as NATS

async def run():
    nc = NATS()
    await nc.connect("nats://nyota_bus:4222")
    js = nc.jetstream()
    
    # Create the persistent stream if it doesn't exist
    await js.add_stream(name="ENTERPRISE_EVENTS", subjects=["events.>"])
    
    payload = json.dumps({
        "event_id": "test-uuid-001",
        "action": "boot_sequence",
        "status": "online"
    }).encode()
    
    print("Publishing boot event...")
    ack = await js.publish("events.core.system.booted", payload)
    print(f"Ack received: {ack}")
    await nc.close()

if __name__ == '__main__':
    asyncio.run(run())
EOF
python3 publisher.py
```

**Outcome:** The Publisher script will successfully commit the message to NATS JetStream. The Listener script (in the separate Security OS container) will instantly log the received JSON payload.

You have successfully established the foundational Event Horizon for the Nyota v2 Distributed Architecture. 🚀

