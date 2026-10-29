# Meal Planner CLI

A local-first CLI that generates weekly meal plans from your pantry ingredients using a configurable OpenAI-compatible endpoint (default: Ollama at `http://localhost:11434/v1`). Plans are saved locally as Markdown or JSON, and grocery lists are exported so you only buy what you are missing.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI tools, books, and practical local-first software. Credit: Asdale Dynamics, LLC.

## Features

- Generate weekly meal plans from pantry ingredients
- Configurable OpenAI-compatible endpoint (Ollama, LM Studio, vLLM, etc.)
- Save plans as JSON and Markdown
- Export grocery lists (ingredients not already in your pantry)
- Manage a local pantry file — no accounts, no API keys required by default
- Tested against a mock endpoint — no secrets and no external network calls needed

## Quick start

Create a pantry file:

```bash
echo '{"ingredients": ["eggs", "bread", "milk", "pasta", "tomato sauce"]}' > pantry.json
```

Generate a 7-day plan (defaults to the local Ollama endpoint):

```bash
python -m meal_planner plan --pantry pantry.json --output meal_plan.json
```

Also export a Markdown plan and a grocery list:

```bash
python -m meal_planner plan --pantry pantry.json --markdown plan.md --grocery grocery_list.md
```

Point at a different OpenAI-compatible endpoint:

```bash
python -m meal_planner plan --endpoint http://localhost:1234/v1 --model hermes-3 --days 5
```

Manage your pantry:

```bash
python -m meal_planner pantry --file pantry.json --show
python -m meal_planner pantry --file pantry.json --add butter garlic cheese
```

View effective configuration:

```bash
python -m meal_planner config
```

## Configuration

Endpoint, model, days, and timeout can be set with environment variables (`MEAL_PLAN_ENDPOINT`, `MEAL_PLAN_MODEL`, `MEAL_PLAN_DAYS`, `MEAL_PLAN_TIMEOUT`, `MEAL_PANTRY_FILE`) or saved to a config file with `meal-plan config --save`. If your endpoint requires a bearer token, set `MEAL_PLAN_API_KEY` — never commit it.

## Local-first

Everything runs on your machine. Plans and grocery lists are saved to local files. The only network call is to your configured local endpoint. The test suite uses a mock endpoint, so nothing is sent to any external service and no API keys are needed.

## Install

```bash
pip install -e .
```

This provides the `meal-plan` console script:

```bash
meal-plan plan --pantry pantry.json --output meal_plan.json
```

## Tests

```bash
python -m pytest tests/
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) is the LLC of Dylan Asdale, a registered nurse turned AI author and founder. The LLC focuses on beginner-friendly AI education, books and guides (including *The Massive AI Manual*), and practical open-source tools that can be published or sold. Dylan explains AI "like a friend would": plain English, step by step, never condescending. Hub site: dylanasdale.github.io.
