"""Pytest fixtures: a mock OpenAI-compatible endpoint serving canned plans."""

from __future__ import annotations

import json
import re
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from meal_planner.client import MealPlannerClient

WEEK_START = date(2026, 11, 2)  # Monday

MEAL_TEMPLATES = {
    "breakfast": ("Scrambled Eggs", ["eggs", "butter"], "Whisk eggs and cook in butter."),
    "lunch": ("Egg Salad Sandwich", ["eggs", "bread", "mayo"], "Mix chopped eggs with mayo on bread."),
    "dinner": ("Pasta with Tomato Sauce", ["pasta", "tomato sauce", "garlic"], "Boil pasta, warm sauce with garlic."),
}


def build_mock_plan(days: int) -> dict:
    plan_days = []
    for i in range(days):
        day_date = WEEK_START + timedelta(days=i)
        meals = {}
        for meal_name, (name, ingredients, instructions) in MEAL_TEMPLATES.items():
            meals[meal_name] = {
                "name": name,
                "ingredients": list(ingredients),
                "instructions": instructions,
            }
        plan_days.append(
            {
                "day": day_date.strftime("%A"),
                "date": day_date.isoformat(),
                "meals": meals,
            }
        )
    return {"week_start": WEEK_START.isoformat(), "days": plan_days}


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        try:
            body_json = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body_json = {}
        text = json.dumps(body_json)
        match = re.search(r"Plan (\d+) days", text)
        days = min(max(int(match.group(1)) if match else 1, 1), 14)
        plan = build_mock_plan(days)
        body = json.dumps({"choices": [{"message": {"content": json.dumps(plan)}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


@pytest.fixture(scope="module")
def mock_endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/v1"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture
def client(mock_endpoint: str) -> MealPlannerClient:
    return MealPlannerClient(endpoint=mock_endpoint, model="test-model")
