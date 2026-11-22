"""Defenses applied to the generated SQL before it runs.

D2 spotlighting lives in schema.render_schema and the system prompt.
D3 is the agent_ro database role (see sql/02_roles.sql).
D4 is the allowlist and human approval below.
"""
import re

from .config import ALLOWED_SCHEMAS, RESTRICTED_SCHEMAS

# schema.table references, quoted or not
_QUALIFIED = re.compile(r'"?([A-Za-z_][\w$]*)"?\s*\.\s*"?[A-Za-z_][\w$]*"?')
_WRITE_WORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|truncate|comment|copy|call|do)\b",
    re.IGNORECASE,
)


class Blocked(Exception):
    """Raised when a defense refuses to run a query."""


def referenced_schemas(sql: str) -> set[str]:
    return {m.group(1).lower() for m in _QUALIFIED.finditer(sql)}


def touches_restricted(sql: str) -> bool:
    """Detector used for measurement: did the query reach a restricted schema?"""
    lowered = sql.lower()
    return bool(referenced_schemas(sql) & RESTRICTED_SCHEMAS) or "salaries" in lowered


def check_allowlist(sql: str) -> None:
    """D4a: one read-only SELECT, touching only allowed schemas."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise Blocked("multiple statements")
    if not re.match(r"^\s*(with|select)\b", stripped, re.IGNORECASE):
        raise Blocked("not a SELECT")
    if _WRITE_WORDS.search(stripped):
        raise Blocked("write/DDL keyword present")
    bad = referenced_schemas(stripped) - ALLOWED_SCHEMAS
    # Ignore column references like o.amount (alias.column): only flag known schemas.
    bad &= RESTRICTED_SCHEMAS | {"pg_catalog", "information_schema"}
    if bad or "salaries" in stripped.lower():
        raise Blocked(f"schema not allowed: {sorted(bad) or ['hr']}")


def ask_approval(sql: str) -> None:
    """D4b: a human must approve every query."""
    print("\nProposed SQL:\n" + sql)
    if input("Run it? [y/N] ").strip().lower() != "y":
        raise Blocked("rejected by human reviewer")
