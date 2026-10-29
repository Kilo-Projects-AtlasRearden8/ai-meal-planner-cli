"""Meal plan generation: prompt construction, model call, response parsing."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from typing import Any

from .client import MealPlannerClient
from .pantry import Pantry

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_NAMES = ("breakfast", "lunch", "dinner")

SYSTEM_PROMPT = """You are a helpful meal-planning assistant. You create weekly meal plans using ingredients from a user's pantry, plus small common staples (salt, pepper, oil, water). Return strictly valid JSON and nothing else.

Schema:
{
  "week_start": "YYYY-MM-DD",
  "days": [
    {
      "day": "Monday",
      "date": "YYYY-MM-DD",
      "meals": {
        "breakfast": {"name": "...", "ingredients": ["..."], "instructions": "..."},
        "lunch": {"name": "...", "ingredients": ["..."], "instructions": "..."},
        "dinner": {"name": "...", "ingredients": ["..."], "instructions": "..."}
      }
    }
  ]
}

Rules: prefer pantry ingredients; keep recipes simple and beginner-friendly; every ingredient must be in the pantry or a common staple; do not give medical or dietary advice; output JSON only."""

USER_TEMPLATE = """Pantry ingredients: {pantry}
Plan {days} days starting {week_start}.
Preferences: {preferences}
Return the meal plan JSON only."""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError(f"Could not parse JSON from model response: {text[:200]}...")


def _normalize_plan(raw: dict[str, Any], week_start: date) -> dict[str, Any]:
    days_raw = raw.get("days") or []
    if not isinstance(days_raw, list):
        days_raw = []
    days = []
    for i, entry in enumerate(days_raw):
        day_date = week_start + timedelta(days=i)
        day_name = WEEK_DAYS[day_date.weekday()]
        meals_raw = entry.get("meals") or {}
        if not isinstance(meals_raw, dict):
            meals_raw = {}
        meals = {}
        for meal_name in MEAL_NAMES:
            meal = meals_raw.get(meal_name) or {}
            if not isinstance(meal, dict):
                meal = {}
            meals[meal_name] = {
                "name": str(meal.get("name", meal_name.title())),
                "ingredients": [str(x) for x in (meal.get("ingredients") or [])],
                "instructions": str(meal.get("instructions", "")),
            }
        days.append({"day": day_name, "date": day_date.isoformat(), "meals": meals})
    return {"week_start": week_start.isoformat(), "days": days}


class MealPlanner:
    def __init__(self, client: MealPlannerClient, pantry: Pantry):
        self.client = client
        self.pantry = pantry

    def generate(
        self,
        days: int = 7,
        week_start: date | None = None,
        preferences: str = "",
    ) -> dict[str, Any]:
        start = week_start or date.today()
        pantry_list = ", ".join(self.pantry.ingredients) or "(none)"
        user = USER_TEMPLATE.format(
            pantry=pantry_list,
            days=days,
            week_start=start.isoformat(),
            preferences=preferences or "(none)",
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ]
        content = self.client.chat_content(messages, temperature=0.7)
        raw = _extract_json(content)
        plan = _normalize_plan(raw, start)
        plan["pantry"] = list(self.pantry.ingredients)
        plan["generated_at"] = date.today().isoformat()
        return plan

    def grocery_list(self, plan: dict[str, Any]) -> list[str]:
        needed: list[str] = []
        for day in plan.get("days", []):
            for meal in day.get("meals", {}).values():
                needed.extend(meal.get("ingredients", []))
        return self.pantry.missing(needed)
