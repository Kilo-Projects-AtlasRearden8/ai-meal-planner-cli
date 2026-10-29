"""Configuration for the meal planner CLI.

Values come from (in priority order): constructor arguments, CLI flags,
environment variables, and a JSON config file. Nothing is ever written to
disk unless the user explicitly saves a config file.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"
DEFAULT_DAYS = 7
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 60
CONFIG_FILE_NAME = "meal-planner.json"


@dataclass
class Config:
    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL
    days: int = DEFAULT_DAYS
    temperature: float = DEFAULT_TEMPERATURE
    timeout: int = DEFAULT_TIMEOUT
    api_key: str | None = None
    pantry_file: str = "pantry.json"

    @classmethod
    def load(cls, config_file: str | None = None) -> "Config":
        path = (
            Path(config_file)
            if config_file
            else Path.home() / ".config" / "meal-planner" / CONFIG_FILE_NAME
        )
        data: dict = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        env = {
            "endpoint": os.environ.get("MEAL_PLAN_ENDPOINT"),
            "model": os.environ.get("MEAL_PLAN_MODEL"),
            "days": os.environ.get("MEAL_PLAN_DAYS"),
            "temperature": os.environ.get("MEAL_PLAN_TEMPERATURE"),
            "timeout": os.environ.get("MEAL_PLAN_TIMEOUT"),
            "api_key": os.environ.get("MEAL_PLAN_API_KEY"),
            "pantry_file": os.environ.get("MEAL_PANTRY_FILE"),
        }
        data = {**data, **{k: v for k, v in env.items() if v is not None}}
        if "days" in data and isinstance(data["days"], str):
            data["days"] = int(data["days"])
        if "temperature" in data and isinstance(data["temperature"], str):
            data["temperature"] = float(data["temperature"])
        if "timeout" in data and isinstance(data["timeout"], str):
            data["timeout"] = int(data["timeout"])
        return cls(
            **{k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        )

    def save(self, config_file: str) -> None:
        path = Path(config_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    def to_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "model": self.model,
            "days": self.days,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "api_key": self.api_key,
            "pantry_file": self.pantry_file,
        }
