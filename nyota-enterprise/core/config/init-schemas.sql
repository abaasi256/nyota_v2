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

-- Revenue OS CRM Tables
CREATE TABLE revenue.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'NEW',
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Revenue OS Permissions Matrix
GRANT ALL PRIVILEGES ON TABLE revenue.leads TO os_revenue;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA revenue TO os_revenue;
