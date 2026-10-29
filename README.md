# Meal Planner CLI

A friendly, local-first command-line tool that turns the ingredients already in
your pantry into a weekly meal plan. It talks to a local OpenAI-compatible
endpoint — Ollama by default — so everything runs on your machine. No accounts,
no API keys, and nothing is sent to any external service.

Made by **Asdale Dynamics, LLC** — beginner-friendly AI tools, books, and
guides. Credit: Asdale Dynamics, LLC.

## Who this is for

Anyone who wants dinner planned without starting from scratch. If you have eggs,
bread, and pasta in the fridge, this tool builds a week of breakfasts, lunches,
and dinners around what you already own — then exports a grocery list of only
what you're missing. It's designed to be approachable: plain English, step by
step, never condescending.

## What you need

- Python 3.9 or newer
- A local OpenAI-compatible endpoint running (Ollama is the default at
  `http://localhost:11434/v1`). You can also point the tool at LM Studio,
  vLLM, or any other OpenAI-compatible server.

No API key is required unless your endpoint demands one.

## Install

From this folder:

```bash
pip install -e .
```

This gives you the `meal-plan` command. You can also run anything with
`python -m meal_planner` instead.

## Step by step: your first plan

**1. Create a pantry file.** List what you already have:

```bash
echo '{"ingredients": ["eggs", "bread", "milk", "pasta", "tomato sauce"]}' > pantry.json
```

**2. Generate a 7-day meal plan** (defaults to the local Ollama endpoint):

```bash
meal-plan plan --pantry pantry.json --output meal_plan.json
```

This saves `meal_plan.json` with breakfast, lunch, and dinner for each day.

**3. Also get a Markdown plan and a grocery list:**

```bash
meal-plan plan --pantry pantry.json --markdown plan.md --grocery grocery_list.md
```

- `plan.md` — a human-readable weekly menu you can print or share.
- `grocery_list.md` — only the ingredients your pantry doesn't already cover,
  with checkboxes for shopping.

**4. Point at a different endpoint or model** (for example LM Studio):

```bash
meal-plan plan --pantry pantry.json --endpoint http://localhost:1234/v1 --model hermes-3 --days 5
```

**5. Manage your pantry:**

```bash
meal-plan pantry --file pantry.json --show
meal-plan pantry --file pantry.json --add butter garlic cheese
meal-plan pantry --file pantry.json --remove eggs
```

**6. Check your configuration:**

```bash
meal-plan config
```

Save it to a file so you don't have to type flags every time:

```bash
meal-plan config --save
```

## Configuration

Settings can come from command flags, environment variables, or a saved config
file (in that priority order).

| Setting | Environment variable | Default |
|---------|----------------------|---------|
| Endpoint URL | `MEAL_PLAN_ENDPOINT` | `http://localhost:11434/v1` |
| Model name | `MEAL_PLAN_MODEL` | `llama3.2` |
| Days to plan | `MEAL_PLAN_DAYS` | `7` |
| Sampling temperature | `MEAL_PLAN_TEMPERATURE` | `0.7` |
| Request timeout (seconds) | `MEAL_PLAN_TIMEOUT` | `60` |
| Pantry file | `MEAL_PANTRY_FILE` | `pantry.json` |
| Bearer token (only if needed) | `MEAL_PLAN_API_KEY` | none |

Never commit `MEAL_PLAN_API_KEY` to version control.

## Export formats

- **JSON** (`--output`) — full plan data, easy to read with other tools.
- **Markdown** (`--markdown`) — a nicely formatted weekly menu.
- **Grocery list** (`--grocery`) — Markdown checklist of ingredients not in
  your pantry.

You can also export a grocery list from a plan you already saved:

```bash
meal-plan grocery-list meal_plan.json --output grocery_list.md
```

## Tests

The test suite uses a mock endpoint, so nothing is sent to any external service
and no API keys are needed:

```bash
python -m pytest tests/
```

## Local-first

Everything runs on your computer. Plans and grocery lists are saved to local
files you control. The only network call is to the endpoint you configure. The
tests use a mock endpoint, so you can verify everything without Ollama running
and without any keys.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) is the LLC of Dylan Asdale,
a registered nurse turned AI author and founder. The LLC focuses on
beginner-friendly AI education, books and guides (including *The Massive AI
Manual*), and practical open-source tools that can be published or sold. Dylan
explains AI "like a friend would": plain English, step by step, never
condescending. Hub site: dylanasdale.github.io.
