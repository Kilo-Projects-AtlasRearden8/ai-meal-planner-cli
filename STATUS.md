# STATUS — Meal Planner CLI

## What was built

A local-first Python CLI (`meal-plan`, package `meal_planner`) that generates
weekly meal plans from pantry ingredients using a configurable OpenAI-compatible
endpoint (default: Ollama at `http://localhost:11434/v1`). No API keys, no
accounts, no external network calls by default; plans and grocery lists are saved
to local files.

Components:
- `meal_planner/client.py` — stdlib (`urllib`) client for `/v1/chat/completions`,
  with bearer-token support and clear connection/HTTP errors
- `meal_planner/planner.py` — builds a strict-JSON prompt, parses/normalizes the
  plan, computes the grocery list (recipe ingredients missing from the pantry),
  and forwards the sampling temperature to the model
- `meal_planner/pantry.py` — load/save/add/remove pantry ingredients (JSON file),
  case-insensitive membership
- `meal_planner/exporters.py` — Markdown, JSON, and grocery-list (Markdown) export
- `meal_planner/cli.py` — argparse CLI: `plan`, `grocery-list`, `pantry`, `config`;
  friendly error messages instead of tracebacks
- `meal_planner/config.py` — config from saved file + env vars
  (`MEAL_PLAN_ENDPOINT`, `MEAL_PLAN_MODEL`, `MEAL_PLAN_DAYS`,
  `MEAL_PLAN_TEMPERATURE`, `MEAL_PLAN_TIMEOUT`, `MEAL_PANTRY_FILE`,
  `MEAL_PLAN_API_KEY`)
- `tests/` — 15 tests against a mock OpenAI-compatible HTTP endpoint (no keys)
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — credits Asdale Dynamics, LLC; warm step-by-step usage,
  configuration table, local-first notes, troubleshooting

Built for Dylan Asdale / Asdale Dynamics, LLC (Indiana, formed Oct 2026):
beginner-friendly, plain English, warm and polished, local-first, no secrets.

## How to run

```bash
# From the project folder
python -m meal_planner --help

# Create a pantry file
echo '{"ingredients": ["eggs", "bread", "milk"]}' > pantry.json

# Generate a 7-day plan (default endpoint: local Ollama)
python -m meal_planner plan --pantry pantry.json --output meal_plan.json

# With Markdown plan and grocery list
python -m meal_planner plan --pantry pantry.json --markdown plan.md --grocery grocery_list.md

# Another OpenAI-compatible endpoint
python -m meal_planner plan --endpoint http://localhost:1234/v1 --model hermes-3 --days 5

# Via the installed console script (pip install -e .)
meal-plan plan --pantry pantry.json --output meal_plan.json

# Tests (mock endpoint, no keys, no network)
python -m pytest tests/
```

Configure with env vars or `meal-plan config --save`.

## Verification results

- `python -m pytest tests/` — **15 passed** (client, planner incl. temperature
  pass-through, exporters, CLI end-to-end via subprocess against mock endpoint,
  missing-endpoint and bad-date friendly-error paths)
- `python -m meal_planner --help / config / pantry` — all subcommands work
- Unreachable endpoint / invalid date → friendly `Error: ...` message, exit 1
  (no traceback)
- `python -m venv /tmp/kilo/venv && pip install -e .` — package builds and
  installs; `meal-plan` console script works (system `pip install -e .` is
  blocked by PEP 668 on this machine; use a venv)
- No `.github/workflows`, no secrets/API keys/personal data in any file
- LICENSE copyright line is exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC

## Known gaps

- Live endpoint not tested against a running Ollama (none running here);
  verified against the mock endpoint instead. You need Ollama (or another
  OpenAI-compatible server) running to generate real plans.
- Config file is only written when you run `config --save`; defaults target
  `http://localhost:11434/v1` / `llama3.2`.
- Model responses are parsed as JSON; malformed model output raises a clear
  error. Fenced code blocks are handled.
- Education-only tool: no medical or dietary advice is given or implied by the
  prompts.
