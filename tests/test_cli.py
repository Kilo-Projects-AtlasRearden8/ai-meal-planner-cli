"""End-to-end CLI tests driven through a subprocess against the mock endpoint."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from meal_planner.pantry import Pantry


def run_cli(args: list[str], endpoint: str | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "meal_planner.cli", *args]
    if endpoint is not None:
        cmd.extend(["--endpoint", endpoint])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_plan_command(tmp_path, mock_endpoint):
    pantry = tmp_path / "pantry.json"
    pantry.write_text(json.dumps({"ingredients": ["eggs", "bread", "pasta"]}))
    out = tmp_path / "plan.json"
    result = run_cli(
        [
            "plan",
            "--pantry",
            str(pantry),
            "--days",
            "1",
            "--week-start",
            "2026-11-02",
            "--output",
            str(out),
            "--markdown",
            str(tmp_path / "plan.md"),
            "--grocery",
            str(tmp_path / "grocery.md"),
        ],
        mock_endpoint,
    )
    assert result.returncode == 0, result.stderr
    plan = json.loads(out.read_text(encoding="utf-8"))
    assert len(plan["days"]) == 1
    assert plan["days"][0]["meals"]["breakfast"]["name"] == "Scrambled Eggs"
    assert (tmp_path / "plan.md").exists()
    assert (tmp_path / "grocery.md").exists()
    grocery_text = (tmp_path / "grocery.md").read_text(encoding="utf-8")
    assert "tomato sauce" in grocery_text
    assert "eggs" not in grocery_text


def test_pantry_command(tmp_path, mock_endpoint):
    pantry = tmp_path / "pantry.json"
    result = run_cli(
        ["pantry", "--file", str(pantry), "--add", "eggs", "bread", "--show"]
    )
    assert result.returncode == 0, result.stderr
    assert "eggs" in result.stdout
    assert "bread" in result.stdout
    data = json.loads(pantry.read_text(encoding="utf-8"))
    assert data["ingredients"] == ["eggs", "bread"]
    pantry = Pantry.load(pantry)
    assert pantry.remove(["eggs"]) == 1
    assert pantry.ingredients == ["bread"]


def test_config_command(mock_endpoint):
    result = run_cli(["config", "--endpoint", mock_endpoint, "--model", "test-model"])
    assert result.returncode == 0, result.stderr
    assert mock_endpoint in result.stdout
    assert "test-model" in result.stdout


def test_missing_endpoint_fails_cleanly(tmp_path):
    pantry = tmp_path / "pantry.json"
    pantry.write_text(json.dumps({"ingredients": ["eggs"]}))
    result = run_cli(
        ["plan", "--pantry", str(pantry), "--endpoint", "http://127.0.0.1:1"]
    )
    assert result.returncode != 0
    assert "Could not reach endpoint" in result.stderr or result.returncode == 1
