# Metadata Injection Lab

**Your data catalog is now a prompt: metadata as an injection surface for LLM agents.**

A fully offline lab showing how database metadata (column and table comments)
flows into a text-to-SQL agent's prompt, and which defenses hold up when that
metadata can't be trusted.

> **Purpose and scope.** This is an educational lab for a graduate cybersecurity
> course. It runs entirely on one laptop against a local, disposable database.
> All data is synthetic. Only use these techniques on systems you own or are
> explicitly authorized to test.

## Architecture

```
Question ──► agent.py ──► reads schema + COMMENTs from Postgres
                 │
                 ├──► builds prompt ──► Ollama (local model) ──► SQL
                 │
                 └──► defenses ──► executes SQL as agent_full or agent_ro
```

| Component | What it is |
|---|---|
| Postgres 16 (Docker) | `public.customers`, `public.orders`, `public.employees`, restricted `hr.salaries` |
| Ollama | local model, default `qwen2.5-coder:7b` (`LAB_MODEL` to change) |
| `lab/agent.py` | ~100-line hand-written text-to-SQL agent |
| `lab/defenses.py` | allowlist, human approval, restricted-schema detector |

## Threat model

Writing metadata is usually granted far more broadly, and reviewed far less, than
reading sensitive data. The agent reads that metadata and acts with its own
database privileges. If the agent's role can read `hr.salaries` and someone who
can't read it can edit a comment, the gap between those two privileges is the risk.

OWASP LLM Top 10 mapping: LLM01 Prompt Injection, LLM02 Sensitive Information
Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency.

## Defenses

| ID | Defense | Where | Type |
|---|---|---|---|
| D1 | Metadata scanner | *(to add)* | prompt-level |
| D2 | Spotlighting: comments wrapped in `<<metadata>>` markers + rule in system prompt | `--spotlight` | prompt-level |
| D3 | Least-privilege read-only role, `public` only | `--role ro` | privilege-level |
| D4a | Query allowlist: single SELECT, allowed schemas only | `--allowlist` | output-level |
| D4b | Human approval before execution | `--approve` | output-level |

## Setup

Requires Docker Desktop, Ollama, Python 3.11+, ~16 GB RAM.

```bash
ollama pull qwen2.5-coder:7b
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
./scripts/reset.sh                 # start Postgres with the clean baseline
python -m scripts.check_env        # verify everything is reachable
```

## Usage

```bash
# Baseline, no defenses
python -m lab.agent "What was total order revenue by region?"

# Show the full prompt so you can see where metadata enters
python -m lab.agent --show-prompt "How many employees are in Sales?"

# All defenses
python -m lab.agent --role ro --spotlight --allowlist "What was total order revenue by region?"
```

Reset to the clean baseline at any time with `./scripts/reset.sh`.

## Results

*(Fill in: attack success rate over N runs per condition.)*

| Condition | Runs | Restricted data reached | Rate |
|---|---|---|---|
| No defense | | | |
| D2 spotlighting | | | |
| D3 read-only role | | | |
| D4a allowlist | | | |
| All combined | | | |

`defenses.touches_restricted()` flags generated SQL that reaches `hr.*`, and
`agent.run(..., quiet=True)` returns a result dict you can log per run.

## License

MIT. See [LICENSE](LICENSE).
