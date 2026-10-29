"""Command-line interface for the meal planner."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .client import MealPlannerClient
from .config import Config
from .exporters import export_grocery_list, export_json, export_markdown
from .pantry import Pantry
from .planner import MealPlanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meal-plan",
        description=(
            "Generate weekly meal plans from pantry ingredients using a local "
            "OpenAI-compatible endpoint (default Ollama)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="Generate a weekly meal plan")
    p_plan.add_argument("--pantry", default="pantry.json", help="Pantry ingredients file")
    p_plan.add_argument("--days", type=int, default=None, help="Number of days")
    p_plan.add_argument("--week-start", help="Start date YYYY-MM-DD (default: today)")
    p_plan.add_argument("--endpoint", help="OpenAI-compatible endpoint URL")
    p_plan.add_argument("--model", help="Model name")
    p_plan.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    p_plan.add_argument("--output", default="meal_plan.json", help="Save plan JSON")
    p_plan.add_argument("--markdown", help="Also save Markdown plan")
    p_plan.add_argument("--grocery", help="Also export grocery list Markdown")
    p_plan.add_argument("--preferences", default="", help="Dietary preferences or notes")

    p_grocery = sub.add_parser("grocery-list", help="Export grocery list from a saved plan")
    p_grocery.add_argument("plan", help="Saved plan JSON file")
    p_grocery.add_argument("--output", default="grocery_list.md", help="Output Markdown file")
    p_grocery.add_argument("--pantry", default="pantry.json", help="Pantry ingredients file")

    p_pantry = sub.add_parser("pantry", help="Manage pantry ingredients")
    p_pantry.add_argument("--file", default="pantry.json", help="Pantry ingredients file")
    p_pantry.add_argument("--show", action="store_true", help="List pantry ingredients")
    p_pantry.add_argument("--add", nargs="+", help="Ingredients to add")
    p_pantry.add_argument("--remove", nargs="+", help="Ingredients to remove")

    p_config = sub.add_parser("config", help="Show or save effective configuration")
    p_config.add_argument("--file", default=None, help="Config file to load/save")
    p_config.add_argument("--endpoint", help="Endpoint to set")
    p_config.add_argument("--model", help="Model to set")
    p_config.add_argument("--save", action="store_true", help="Save configuration to file")

    return parser


def _cmd_plan(args: argparse.Namespace) -> int:
    config = Config.load()
    endpoint = args.endpoint or config.endpoint
    model = args.model or config.model
    days = args.days if args.days is not None else config.days
    client = MealPlannerClient(
        endpoint=endpoint,
        model=model,
        api_key=config.api_key,
        timeout=config.timeout,
    )
    pantry = Pantry.load(args.pantry)
    week_start = date.fromisoformat(args.week_start) if args.week_start else None
    planner = MealPlanner(client=client, pantry=pantry)
    plan = planner.generate(days=days, week_start=week_start, preferences=args.preferences)
    export_json(plan, args.output)
    print(f"Saved plan to {args.output}")
    if args.markdown:
        export_markdown(plan, args.markdown)
        print(f"Saved Markdown plan to {args.markdown}")
    if args.grocery:
        grocery = planner.grocery_list(plan)
        export_grocery_list(grocery, args.grocery, plan=plan)
        print(f"Saved grocery list to {args.grocery}")
    return 0


def _cmd_grocery_list(args: argparse.Namespace) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    pantry = Pantry.load(args.pantry)
    needed: list[str] = []
    for day in plan.get("days", []):
        for meal in day.get("meals", {}).values():
            needed.extend(meal.get("ingredients", []))
    grocery = pantry.missing(needed)
    export_grocery_list(grocery, args.output, plan=plan)
    print(f"Saved grocery list to {args.output}")
    return 0


def _cmd_pantry(args: argparse.Namespace) -> int:
    pantry = Pantry.load(args.file)
    changed = False
    if args.add:
        pantry.add(args.add)
        changed = True
    if args.remove:
        pantry.remove(args.remove)
        changed = True
    if changed:
        pantry.save(args.file)
        print(f"Updated {args.file}")
    if args.show or not changed:
        if pantry.ingredients:
            for item in pantry.ingredients:
                print(item)
        else:
            print("(empty)")
    return 0


def _cmd_config(args: argparse.Namespace) -> int:
    config = Config.load(args.file)
    if args.endpoint:
        config.endpoint = args.endpoint
    if args.model:
        config.model = args.model
    if args.save:
        target = args.file or str(Path.home() / ".config" / "meal-planner" / "meal-planner.json")
        config.save(target)
        print(f"Saved config to {target}")
    else:
        print(f"endpoint: {config.endpoint}")
        print(f"model: {config.model}")
        print(f"days: {config.days}")
        print(f"temperature: {config.temperature}")
        print(f"timeout: {config.timeout}")
        print(f"pantry_file: {config.pantry_file}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "plan":
        return _cmd_plan(args)
    if args.command == "grocery-list":
        return _cmd_grocery_list(args)
    if args.command == "pantry":
        return _cmd_pantry(args)
    if args.command == "config":
        return _cmd_config(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
