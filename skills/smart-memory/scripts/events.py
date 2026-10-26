#!/usr/bin/env python3
"""Append-only event log for a project's agent threads: what was decided, found, tried.

  events.py add --type decision --summary "Kept FTS5 over embeddings" [--thread ID] ...
  events.py list [--type error] [--thread ID] [--grep relay] [--json]
  events.py brief                  # what a new thread must know before it starts
  events.py validate [FILE]        # schema + debugging-discipline findings

The log lives at <project>/.memory/events.jsonl (override with --file). recall.py indexes
it alongside agent transcripts, so a decision logged here surfaces in later threads.

Exit codes: 0 pass, 1 findings (validate) or a rejected event (add), 2 usage error.
Standard library only.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

TYPES = {
    "goal": "what this thread is for, in the user's words",
    "decision": "a choice made, and the alternative rejected",
    "finding": "something verified true about the code, data or environment",
    "hypothesis": "a single root-cause theory under test (systematic-debugging phase 3)",
    "attempt": "one minimal change made to test a hypothesis, with its outcome",
    "error": "an observed failure: message, command, file:line",
    "fix": "the root-cause fix for an error; must name the error it resolves",
    "preference": "how the user wants things done; never ask for it again",
    "question": "something open that needs the user or more evidence",
    "answer": "the resolution of a question; must name the question",
    "handoff": "end-of-thread state for the next thread: done, open, next step",
}
STATUSES = ("open", "resolved", "failed", "superseded")
OUTCOMES = ("passed", "failed", "inconclusive")
MAX_SUMMARY = 200
SECRET = re.compile(
    r"(vcp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9\-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def die(msg):
    print("events: %s" % msg, file=sys.stderr)
    sys.exit(2)


def default_file():
    return os.path.join(os.getcwd(), ".memory", "events.jsonl")


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.strip():
                rows.append((n, line))
    return rows


def parse(rows):
    events, bad = [], []
    for n, line in rows:
        try:
            events.append((n, json.loads(line)))
        except ValueError as exc:
            bad.append((n, "not valid JSON (%s) — rewrite the line as one JSON object" % exc.msg))
    return events, bad


def check_event(e, ids):
    """Findings for one event, as (message, fix) pairs."""
    out = []
    if not isinstance(e, dict):
        return [("event is not a JSON object", "write one object per line")]
    for field in ("id", "ts", "thread", "type", "summary"):
        if not e.get(field):
            out.append(("missing `%s`" % field, "add it; `events.py add` fills id and ts"))
    t = e.get("type")
    if t and t not in TYPES:
        out.append(("unknown type `%s`" % t, "use one of: %s" % ", ".join(TYPES)))
    s = e.get("summary") or ""
    if len(s) > MAX_SUMMARY:
        out.append(("summary is %d chars" % len(s), "keep it under %d; put the rest in `detail`" % MAX_SUMMARY))
    if e.get("ts"):
        try:
            dt.datetime.fromisoformat(str(e["ts"]).replace("Z", "+00:00"))
        except ValueError:
            out.append(("`ts` is not ISO 8601: %s" % e["ts"], "use e.g. 2026-10-26T18:00:00Z"))
    if e.get("status") and e["status"] not in STATUSES:
        out.append(("unknown status `%s`" % e["status"], "use one of: %s" % ", ".join(STATUSES)))
    if t == "fix" and not e.get("resolves"):
        out.append(("a fix that names no error", "set `resolves` to the error event's id — no fix without a root cause"))
    if t == "answer" and not e.get("resolves"):
        out.append(("an answer that names no question", "set `resolves` to the question event's id"))
    if t == "attempt":
        if not e.get("tests"):
            out.append(("an attempt that tests no hypothesis", "set `tests` to the hypothesis event's id"))
        if e.get("outcome") not in OUTCOMES:
            out.append(("attempt outcome is `%s`" % e.get("outcome"), "set `outcome` to passed, failed or inconclusive"))
    for ref in ("resolves", "tests", "supersedes"):
        if e.get(ref) and e[ref] not in ids:
            out.append(("`%s` points at unknown event %s" % (ref, e[ref]), "reference an id earlier in the log"))
    blob = json.dumps(e)
    if SECRET.search(blob):
        out.append(("event contains a secret-shaped token", "remove it; memory is never the place for a credential"))
    return out


def discipline(events):
    """Cross-event findings that enforce systematic-debugging across threads."""
    out = []
    by_id = {e.get("id"): e for _, e in events}
    failed_per_error = {}
    for n, e in events:
        if e.get("type") == "attempt" and e.get("outcome") == "failed":
            hyp = by_id.get(e.get("tests")) or {}
            root = hyp.get("about") or e.get("about") or hyp.get("id")
            failed_per_error.setdefault(root, []).append(n)
    fixed = set()
    for _, e in events:
        if e.get("type") == "fix" and e.get("resolves"):
            fixed.add(e["resolves"])
            fixed.add((by_id.get(e["resolves"]) or {}).get("about"))
    for root, lines in failed_per_error.items():
        if len(lines) >= 3 and root not in fixed:
            out.append((lines[-1], "3+ failed attempts on %s with no fix" % root,
                        "stop fixing: question the architecture with the user (systematic-debugging phase 4.5)"))
    return out


def cmd_validate(path):
    rows = load(path)
    if not rows:
        print("%s: no events" % path)
        return 0
    events, bad = parse(rows)
    findings = list(bad)
    ids = set()
    for n, e in events:
        for msg, fix in check_event(e, ids):
            findings.append((n, "%s — %s" % (msg, fix)))
        if isinstance(e, dict) and e.get("id"):
            if e["id"] in ids:
                findings.append((n, "duplicate id %s — events are append-only, never rewrite one" % e["id"]))
            ids.add(e["id"])
    for n, msg, fix in discipline(events):
        findings.append((n, "%s — %s" % (msg, fix)))
    for n, msg in sorted(findings):
        print("%s:%d: %s" % (path, n, msg))
    print("%d event(s), %d finding(s)" % (len(events), len(findings)))
    return 1 if findings else 0


def cmd_add(a):
    path = a.file
    events, _ = parse(load(path))
    ids = {e.get("id") for _, e in events if isinstance(e, dict)}
    e = {"ts": a.ts or now_iso(), "thread": a.thread or os.environ.get("SMART_MEMORY_THREAD") or "default",
         "type": a.type, "summary": a.summary.strip()}
    for key in ("detail", "status", "resolves", "tests", "supersedes", "outcome", "about"):
        val = getattr(a, key)
        if val:
            e[key] = val
    if a.files:
        e["files"] = [f.strip() for f in a.files.split(",") if f.strip()]
    if a.tags:
        e["tags"] = [t.strip() for t in a.tags.split(",") if t.strip()]
    e["id"] = a.type[:3] + "-" + hashlib.sha1(json.dumps(e, sort_keys=True).encode()).hexdigest()[:8]
    problems = check_event(e, ids)
    if problems:
        for msg, fix in problems:
            print("rejected: %s — %s" % (msg, fix), file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(e["id"])
    return 0


def cmd_list(a):
    events, _ = parse(load(a.file))
    sel = []
    for _, e in events:
        if a.type and e.get("type") != a.type:
            continue
        if a.thread and e.get("thread") != a.thread:
            continue
        if a.grep and a.grep.lower() not in json.dumps(e).lower():
            continue
        sel.append(e)
    if a.json:
        print(json.dumps(sel, indent=2, ensure_ascii=False))
    else:
        for e in sel:
            print("%s  %-10s %-12s %s" % (e.get("ts", "?")[:16], e.get("type"), e.get("id"), e.get("summary")))
    return 0


def cmd_brief(a):
    """Everything still true and still open, newest first, for the start of a new thread."""
    events, _ = parse(load(a.file))
    events = [e for _, e in events if isinstance(e, dict)]
    closed = {e.get("resolves") for e in events if e.get("resolves")}
    closed |= {e.get("supersedes") for e in events if e.get("supersedes")}
    closed |= {e.get("tests") for e in events if e.get("type") == "attempt" and e.get("outcome") == "passed"}
    live = [e for e in events if e.get("id") not in closed and e.get("status") not in ("resolved", "superseded")]
    sections = (
        ("Preferences (never ask again)", ("preference",)),
        ("Decisions in force", ("decision",)),
        ("Verified findings", ("finding",)),
        ("Open errors", ("error",)),
        ("Open hypotheses", ("hypothesis",)),
        ("Open questions", ("question",)),
        ("Last handoff", ("handoff",)),
    )
    print("# Memory brief — %s" % a.file)
    for title, kinds in sections:
        rows = [e for e in live if e.get("type") in kinds]
        if title == "Last handoff":
            rows = rows[-1:]
        if not rows:
            continue
        print("\n## %s" % title)
        for e in reversed(rows[-8:]):
            print("- [%s] %s (%s, thread %s)" % (e["id"], e["summary"], e.get("ts", "?")[:10], e.get("thread")))
    warnings = discipline([(0, e) for e in events])
    if warnings:
        print("\n## Stop signs")
        for _, msg, fix in warnings:
            print("- %s — %s" % (msg, fix))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", default=None, help="event log (default ./.memory/events.jsonl)")
    sub = ap.add_subparsers(dest="cmd")

    add = sub.add_parser("add")
    add.add_argument("--type", required=True, choices=sorted(TYPES))
    add.add_argument("--summary", required=True)
    add.add_argument("--thread")
    add.add_argument("--detail")
    add.add_argument("--files")
    add.add_argument("--tags")
    add.add_argument("--status", choices=STATUSES)
    add.add_argument("--resolves")
    add.add_argument("--tests")
    add.add_argument("--about", help="what an error or hypothesis is about, to group attempts")
    add.add_argument("--outcome", choices=OUTCOMES)
    add.add_argument("--supersedes")
    add.add_argument("--ts")

    ls = sub.add_parser("list")
    ls.add_argument("--type", choices=sorted(TYPES))
    ls.add_argument("--thread")
    ls.add_argument("--grep")
    ls.add_argument("--json", action="store_true")

    sub.add_parser("brief")
    val = sub.add_parser("validate")
    val.add_argument("path", nargs="?")

    a = ap.parse_args()
    a.file = a.file or default_file()
    if a.cmd == "add":
        sys.exit(cmd_add(a))
    if a.cmd == "list":
        sys.exit(cmd_list(a))
    if a.cmd == "brief":
        sys.exit(cmd_brief(a))
    if a.cmd == "validate":
        sys.exit(cmd_validate(a.path or a.file))
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()
