"""Export plans and grocery lists to Markdown and JSON files."""

from __future__ import annotations

import json
from pathlib import Path

MEAL_NAMES = ("breakfast", "lunch", "dinner")


def export_json(plan: dict, path: str | Path) -> Path:
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return p


def export_markdown(plan: dict, path: str | Path) -> Path:
    lines = [f"# Weekly Meal Plan — {plan.get('week_start')}"]
    generated = plan.get("generated_at")
    if generated:
        lines.append(f"Generated: {generated}")
    lines.append("")
    lines.append("## Pantry")
    for item in plan.get("pantry", []):
        lines.append(f"- {item}")
    lines.append("")
    for day in plan.get("days", []):
        lines.append(f"## {day.get('day', 'Day')} — {day.get('date', '')}")
        for meal_name in MEAL_NAMES:
            meal = day.get("meals", {}).get(meal_name, {}) or {}
            lines.append(f"### {meal_name.title()}: {meal.get('name', '')}")
            ingredients = meal.get("ingredients") or []
            if ingredients:
                lines.append("Ingredients: " + ", ".join(ingredients))
            instructions = meal.get("instructions")
            if instructions:
                lines.append(f"Instructions: {instructions}")
            lines.append("")
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def export_grocery_list(grocery: list[str], path: str | Path, plan: dict | None = None) -> Path:
    lines = ["# Grocery List"]
    if plan:
        lines.append(f"For week starting {plan.get('week_start', '')}")
    lines.append("")
    if grocery:
        for item in grocery:
            lines.append(f"- [ ] {item}")
    else:
        lines.append("_All ingredients are already in your pantry._")
    lines.append("")
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
