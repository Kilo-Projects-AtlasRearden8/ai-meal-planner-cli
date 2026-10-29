"""Pantry ingredient store: load, save, add, remove, and diff against recipes."""

from __future__ import annotations

import json
from pathlib import Path


class Pantry:
    """A list of ingredient strings persisted to a JSON file."""

    def __init__(self, ingredients: list[str] | None = None, path: str | Path | None = None):
        self.ingredients = [str(i).strip() for i in (ingredients or []) if str(i).strip()]
        self.path = Path(path) if path else None

    @classmethod
    def load(cls, path: str | Path) -> "Pantry":
        p = Path(path)
        if not p.exists():
            return cls(path=p)
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            ingredients = data.get("ingredients", [])
        elif isinstance(data, list):
            ingredients = data
        else:
            ingredients = []
        return cls(
            ingredients=[str(i).strip() for i in ingredients if str(i).strip()],
            path=p,
        )

    def save(self, path: str | Path | None = None) -> None:
        target = Path(path) if path else self.path
        if target is None:
            raise ValueError("No pantry path specified")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"ingredients": self.ingredients}, indent=2) + "\n",
            encoding="utf-8",
        )

    def add(self, items: list[str]) -> int:
        added = 0
        for item in items:
            item = item.strip()
            if item and item not in self.ingredients:
                self.ingredients.append(item)
                added += 1
        return added

    def remove(self, items: list[str]) -> int:
        before = len(self.ingredients)
        self.ingredients = [i for i in self.ingredients if i not in items]
        return before - len(self.ingredients)

    def contains(self, item: str) -> bool:
        lower = {i.lower() for i in self.ingredients}
        return item.strip().lower() in lower

    def missing(self, needed: list[str]) -> list[str]:
        """Return ingredients from ``needed`` that are not in the pantry."""
        lower = {i.lower() for i in self.ingredients}
        return [n for n in needed if n and n.strip().lower() not in lower]
