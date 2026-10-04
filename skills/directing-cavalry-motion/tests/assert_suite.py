#!/usr/bin/env python3
"""Fail closed until a real Cavalry baseline run is on disk.

This does not talk to Cavalry and does not invent scene results.
It does two jobs:

1. Prove the scorer notices the independent-squares anti-pattern on
   labeled synthetic fixtures.
2. Reject every evaluation scenario whose baseline artifact is missing
   or lacks evidence files that exist in the repo.

Exit 0 only when every scenario has a real baseline. Exit 1 when the
suite is incomplete or a fixture check breaks. Exit 2 on usage errors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENARIOS = ROOT / "scenarios"
FIXTURES = ROOT / "fixtures"
BASELINES = ROOT / "baseline-results"

REQUIRED_SCENARIO_KEYS = (
    "id",
    "title",
    "prompt",
    "agent_sees",
    "repeat_prompt",
    "expected_graph",
    "assertions",
    "hypothesis",
)

REQUIRED_EVIDENCE = ("tool_transcript", "scene_graph", "renders")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("%s must be a JSON object" % path)
    return data


def independent_squares(graph: dict) -> bool:
    """True when three or more source shapes exist and no duplicator does."""
    nodes = graph.get("nodes") or []
    sources = [node for node in nodes if node.get("role") == "source-geometry"]
    duplicators = [node for node in nodes if node.get("role") == "duplicator"]
    return len(sources) >= 3 and len(duplicators) == 0


def check_fixtures() -> list[str]:
    failures = []
    bad = load_json(FIXTURES / "01-independent-squares.json")
    good = load_json(FIXTURES / "01-one-source-duplicator.json")
    for fixture in (bad, good):
        if fixture.get("kind") != "synthetic-fixture" or fixture.get("not_an_agent_run") is not True:
            failures.append("fixture %s is not labeled as synthetic" % fixture.get("id"))
    if not independent_squares(bad):
        failures.append("detector missed the independent-squares fixture")
    if independent_squares(good):
        failures.append("detector flagged the one-source duplicator fixture")
    return failures


def check_scenarios() -> list[str]:
    failures = []
    paths = sorted(SCENARIOS.glob("*.json"))
    if len(paths) != 7:
        failures.append("expected 7 scenarios, found %d" % len(paths))
    seen = set()
    for path in paths:
        try:
            scenario = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append("%s: %s" % (path.name, exc))
            continue
        missing = [key for key in REQUIRED_SCENARIO_KEYS if key not in scenario]
        if missing:
            failures.append("%s missing keys: %s" % (path.name, ", ".join(missing)))
            continue
        scenario_id = scenario["id"]
        if scenario_id in seen:
            failures.append("duplicate scenario id %s" % scenario_id)
        seen.add(scenario_id)
        if scenario["agent_sees"] != "prompt-only":
            failures.append("%s must hide assertions from the agent" % scenario_id)
        if not scenario["assertions"]:
            failures.append("%s has no assertions" % scenario_id)
        hypothesis = scenario["hypothesis"]
        if hypothesis.get("not_a_measurement") is not True:
            failures.append("%s hypothesis is not marked as unmeasured" % scenario_id)
        graph_path = (ROOT / scenario["expected_graph"]).resolve()
        if not graph_path.is_file():
            failures.append("%s expected graph missing: %s" % (scenario_id, scenario["expected_graph"]))
        else:
            graph = load_json(graph_path)
            if graph.get("scenario_id") != scenario_id:
                failures.append("%s expected graph id mismatch" % scenario_id)
            if graph.get("runtime_verified") is not False:
                failures.append("%s expected graph must stay runtime_verified false" % scenario_id)
        result_path = BASELINES / ("%s.json" % scenario_id)
        if not result_path.is_file():
            failures.append(
                "%s: no baseline run at %s"
                % (scenario_id, result_path.relative_to(ROOT))
            )
            continue
        result = load_json(result_path)
        if result.get("kind") != "agent-run":
            failures.append("%s baseline is not an agent-run" % scenario_id)
            continue
        evidence = result.get("evidence") or {}
        for key in REQUIRED_EVIDENCE:
            rel = evidence.get(key)
            if not rel:
                failures.append("%s baseline missing evidence.%s" % (scenario_id, key))
                continue
            target = (ROOT / rel).resolve()
            if not target.exists():
                failures.append("%s evidence file does not exist: %s" % (scenario_id, rel))
    return failures


def main() -> int:
    if len(sys.argv) != 1:
        print("usage: assert_suite.py", file=sys.stderr)
        return 2
    failures = []
    try:
        failures.extend(check_fixtures())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        failures.append("fixture check: %s" % exc)
    if not any(item.startswith("detector") or item.startswith("fixture") for item in failures):
        print("ok    fixture detector flags eight independent squares")
        print("ok    fixture detector accepts one source plus a duplicator")
    failures.extend(check_scenarios())
    for item in failures:
        print("FAIL  %s" % item)
    if failures:
        print("%d failed" % len(failures))
        return 1
    print("all scenarios have evidenced baseline runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
