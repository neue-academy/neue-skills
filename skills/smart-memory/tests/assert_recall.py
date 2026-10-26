#!/usr/bin/env python3
"""Recall regression suite against a fixture home. Exit 0 pass, 1 fail.

  python3 skills/smart-memory/tests/assert_recall.py
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RECALL = os.path.join(HERE, "..", "scripts", "recall.py")
HOME = os.path.join(HERE, "fixtures", "home")
NOW = "2026-10-26T18:00:00Z"
FAILS = []


def run(*args, stdin=None, index):
    cmd = [sys.executable, RECALL, "--home", HOME, "--index", index, "--now", NOW,
           "--sources", "cursor,claude"] + list(args)
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True)


def check(label, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (label, detail))


def main():
    cases = json.load(open(os.path.join(HERE, "gate-cases.json"), encoding="utf-8"))["cases"]
    for c in cases:
        out = subprocess.run([sys.executable, RECALL, "--gate-only", "--json", c["prompt"]],
                             capture_output=True, text=True).stdout
        got = json.loads(out)["verdict"]
        check("gate", got == c["expect"], "%r → %s, expected %s" % (c["prompt"], got, c["expect"]))

    with tempfile.TemporaryDirectory() as tmp:
        index = os.path.join(tmp, "index.db")

        r = json.loads(run("the relay is stuck reconnecting again", "--cwd", "/work/relay",
                           "--session", "ffff0000", "--json", index=index).stdout)
        sessions = {e["session"] for e in r["excerpts"]}
        check("finds the past relay fix", r["verdict"] == "found" and "a1b2c3d4-relay-fix" in sessions, r)
        check("never searches the current session", not any(s.startswith("ffff0000") for s in sessions))
        check("a go-ahead joins the exchange it continues",
              any("4f2e9a1" in e["agent"] and "Root cause" in e["agent"] for e in r["excerpts"]))
        check("dates the excerpt", r["excerpts"] and r["excerpts"][0]["when"] == "last week")

        r = json.loads(run("migrate the invoices table to postgres", "--cwd", "/work/relay",
                           "--json", index=index).stdout)
        check("stays silent on unrelated work", r["verdict"] == "none", r["verdict"])

        r = json.loads(run("set up the release workflow signing", "--cwd", "/work/relay",
                           "--json", index=index).stdout)
        check("folder scope does not leak other projects", r["verdict"] == "none", r["verdict"])

        r = json.loads(run("set up the release workflow signing the way we did in the other app",
                           "--cwd", "/work/relay", "--json", index=index).stdout)
        check("cross-project prompt reaches every folder",
              r["verdict"] == "found" and r["excerpts"][0]["project"] == "work-billing", r)
        blob = json.dumps(r)
        check("redacts secrets from excerpts", "sk-test_" not in blob and "[redacted]" in blob)

        p = run("--hook", "claude", index=index, stdin=json.dumps(
            {"prompt": "the relay is stuck reconnecting again", "cwd": "/work/relay",
             "session_id": "ffff0000-current"}))
        try:
            ctx = json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]
        except (ValueError, KeyError):
            ctx = ""
        check("hook injects <past-sessions>", p.returncode == 0 and ctx.startswith("<past-sessions"), p.stdout[:200])

        transcript = os.path.join(HOME, ".cursor", "projects", "work-relay", "agent-transcripts",
                                  "ffff0000-current", "ffff0000-current.jsonl")
        p = run("--hook", "claude", index=index, stdin=json.dumps(
            {"prompt": "the backoff first", "cwd": "/work/relay", "transcript_path": transcript}))
        check("a reply to the agent's question is left alone", p.returncode == 0 and not p.stdout.strip())

        p = run("--hook", "claude", index=index, stdin="not json")
        check("a broken hook payload never blocks the prompt", p.returncode == 0 and not p.stdout.strip())

        p = run("--limit", "0", "x y z", index=index)
        check("bad usage exits 2", p.returncode == 2)

    for f in FAILS:
        print("FAIL", f)
    print("%d recall check(s) failed" % len(FAILS) if FAILS else "all recall checks passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
