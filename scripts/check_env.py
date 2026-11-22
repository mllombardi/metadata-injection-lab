"""Confirm Postgres, both agent roles and Ollama are reachable before a demo."""
import sys

import ollama
import psycopg

from lab.config import DSN, MODEL

ok = True

for role in ("full", "ro"):
    try:
        with psycopg.connect(DSN[role]) as conn:
            n = conn.execute("SELECT count(*) FROM public.orders").fetchone()[0]
        print(f"[ok]   Postgres as agent_{role}: {n} orders")
    except Exception as e:
        ok = False
        print(f"[fail] Postgres as agent_{role}: {e}")

try:
    with psycopg.connect(DSN["ro"]) as conn:
        conn.execute("SELECT * FROM hr.salaries LIMIT 1")
    ok = False
    print("[fail] agent_ro can read hr.salaries (it should not)")
except psycopg.Error:
    print("[ok]   agent_ro is blocked from hr.salaries")

try:
    names = [m.model for m in ollama.list().models]
    if any(n.startswith(MODEL) for n in names):
        print(f"[ok]   Ollama has {MODEL}")
    else:
        ok = False
        print(f"[fail] Ollama is running but {MODEL} is missing. Run: ollama pull {MODEL}")
except Exception as e:
    ok = False
    print(f"[fail] Ollama: {e}")

sys.exit(0 if ok else 1)
