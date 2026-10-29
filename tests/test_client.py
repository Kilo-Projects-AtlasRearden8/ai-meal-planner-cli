"""Tests for the OpenAI-compatible HTTP client."""

from __future__ import annotations

import json

from meal_planner.client import MealPlannerClient


def test_chat_content_returns_text(client):
    content = client.chat_content([{"role": "user", "content": "make a plan"}])
    data = json.loads(content)
    assert data["days"][0]["meals"]["breakfast"]["name"] == "Scrambled Eggs"
    assert client.endpoint.endswith("/v1")


def test_chat_raw_response(client):
    response = client.chat([{"role": "user", "content": "plan"}])
    assert "choices" in response
    assert response["choices"][0]["message"]["content"]
