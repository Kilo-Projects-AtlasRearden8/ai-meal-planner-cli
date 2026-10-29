"""Tests for Markdown/JSON/grocery-list exporters."""

from __future__ import annotations

import json

from meal_planner.exporters import export_grocery_list, export_json, export_markdown

PLAN = {
    "week_start": "2026-11-02",
    "generated_at": "2026-10-29",
    "pantry": ["eggs"],
    "days": [
        {
            "day": "Monday",
            "date": "2026-11-02",
            "meals": {
                "breakfast": {
                    "name": "Scrambled Eggs",
                    "ingredients": ["eggs", "butter"],
                    "instructions": "Whisk eggs and cook in butter.",
                },
                "lunch": {
                    "name": "Toast",
                    "ingredients": ["bread"],
                    "instructions": "Toast bread.",
                },
                "dinner": {
                    "name": "Pasta",
                    "ingredients": ["pasta"],
                    "instructions": "Boil pasta.",
                },
            },
        }
    ],
}


def test_export_json(tmp_path):
    out = tmp_path / "plan.json"
    export_json(PLAN, out)
    assert json.loads(out.read_text(encoding="utf-8"))["week_start"] == "2026-11-02"


def test_export_markdown(tmp_path):
    out = tmp_path / "plan.md"
    export_markdown(PLAN, out)
    text = out.read_text(encoding="utf-8")
    assert "# Weekly Meal Plan" in text
    assert "Scrambled Eggs" in text
    assert "Butter" in text or "butter" in text
    assert "Whisk eggs and cook in butter" in text


def test_export_grocery_list(tmp_path):
    out = tmp_path / "grocery.md"
    export_grocery_list(["bread", "pasta"], out, plan=PLAN)
    text = out.read_text(encoding="utf-8")
    assert "- [ ] bread" in text
    assert "- [ ] pasta" in text
    assert "2026-11-02" in text


def test_export_grocery_list_empty(tmp_path):
    out = tmp_path / "grocery.md"
    export_grocery_list([], out, plan=PLAN)
    assert "already in your pantry" in out.read_text(encoding="utf-8")
