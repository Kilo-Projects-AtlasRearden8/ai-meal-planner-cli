"""Tests for the meal planner (prompt, parsing, normalization, grocery diff)."""

from __future__ import annotations

from datetime import date

from meal_planner.pantry import Pantry
from meal_planner.planner import MealPlanner


def test_generate_plan(client):
    pantry = Pantry(ingredients=["eggs", "bread", "pasta"])
    planner = MealPlanner(client=client, pantry=pantry)
    plan = planner.generate(days=1, week_start=date(2026, 11, 2))
    assert plan["week_start"] == "2026-11-02"
    assert len(plan["days"]) == 1
    day = plan["days"][0]
    assert day["day"] == "Monday"
    assert day["date"] == "2026-11-02"
    assert set(day["meals"]) == {"breakfast", "lunch", "dinner"}
    assert plan["pantry"] == ["eggs", "bread", "pasta"]
    assert "generated_at" in plan


def test_grocery_excludes_pantry_items(client):
    pantry = Pantry(ingredients=["eggs", "bread", "pasta"])
    planner = MealPlanner(client=client, pantry=pantry)
    plan = planner.generate(days=1)
    grocery = planner.grocery_list(plan)
    assert "eggs" not in grocery
    assert "bread" not in grocery
    assert "pasta" not in grocery
    assert "tomato sauce" in grocery
    assert "garlic" in grocery
    assert "butter" in grocery


def test_grocery_empty_when_everything_in_pantry(client):
    pantry = Pantry(
        ingredients=[
            "eggs",
            "butter",
            "bread",
            "mayo",
            "pasta",
            "tomato sauce",
            "garlic",
            "salt",
            "pepper",
            "oil",
            "water",
        ]
    )
    planner = MealPlanner(client=client, pantry=pantry)
    plan = planner.generate(days=1)
    assert planner.grocery_list(plan) == []


def test_multiple_days(client):
    pantry = Pantry(ingredients=["eggs"])
    planner = MealPlanner(client=client, pantry=pantry)
    plan = planner.generate(days=3, week_start=date(2026, 11, 2))
    assert [d["day"] for d in plan["days"]] == ["Monday", "Tuesday", "Wednesday"]
    assert [d["date"] for d in plan["days"]] == [
        "2026-11-02",
        "2026-11-03",
        "2026-11-04",
    ]
