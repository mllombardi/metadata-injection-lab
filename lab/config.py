import os

MODEL = os.getenv("LAB_MODEL", "qwen2.5-coder:7b")

_HOST = os.getenv("LAB_DB_HOST", "localhost")
DSN = {
    "full": f"host={_HOST} dbname=labdb user=agent_full password=agent_full",
    "ro":   f"host={_HOST} dbname=labdb user=agent_ro password=agent_ro",
}

# Schemas the agent is allowed to query when the allowlist defense is on.
ALLOWED_SCHEMAS = {"public"}
RESTRICTED_SCHEMAS = {"hr"}
