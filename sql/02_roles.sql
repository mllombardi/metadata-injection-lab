-- Two agent roles, so you can compare privilege levels.

-- agent_full: over-privileged. Can read public AND hr.
-- This is the "excessive agency" configuration (OWASP LLM06).
CREATE ROLE agent_full LOGIN PASSWORD 'agent_full';
GRANT USAGE  ON SCHEMA public, hr TO agent_full;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_full;
GRANT SELECT ON ALL TABLES IN SCHEMA hr     TO agent_full;

-- agent_ro: least privilege (defense D3). Read-only, public schema only.
CREATE ROLE agent_ro LOGIN PASSWORD 'agent_ro';
GRANT USAGE  ON SCHEMA public TO agent_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_ro;
REVOKE ALL   ON SCHEMA hr FROM agent_ro;
ALTER ROLE agent_ro SET default_transaction_read_only = on;
ALTER ROLE agent_ro SET statement_timeout = '5s';
