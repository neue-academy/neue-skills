#!/usr/bin/env node
/**
 * Validate a generated capability map: every entry carries the required fields
 * with sane values, and the map is honest about missing sources.
 *
 * Usage:   node validate-capabilities.ts <map.json>
 * Exit:    0 valid, 1 invalid, 2 usage/IO error.
 */

import { readFileSync } from "node:fs";

const REQUIRED = [
  "namespace",
  "method",
  "signature",
  "category",
  "returnType",
  "mutatesScene",
  "securityLevel",
  "mcpCoverage",
  "versionVerified",
  "testCoverage",
  "limitations",
  "sourceUrl",
] as const;

const SECURITY = new Set(["read", "mutate", "raw-exec", "unknown"]);
const COVERAGE = new Set(["direct-tool", "via-execute_script", "none"]);
const TESTCOV = new Set(["none", "fixture", "live"]);

function main(): number {
  const path = process.argv[2];
  if (!path) {
    console.error("usage: validate-capabilities.ts <map.json>");
    return 2;
  }
  let map: any;
  try {
    map = JSON.parse(readFileSync(path, "utf8"));
  } catch (err) {
    console.error("cannot read %s: %s", path, (err as Error).message);
    return 2;
  }

  const problems: string[] = [];
  if (!Array.isArray(map.entries)) {
    console.error("FAIL  map has no entries array");
    return 1;
  }
  if (map.partial !== (Array.isArray(map.missingSources) && map.missingSources.length > 0)) {
    problems.push("partial flag disagrees with missingSources");
  }
  if (map.entries.length === 0 && map.partial !== true) {
    problems.push("empty entry list must set partial:true (no data is not zero capabilities)");
  }

  const seen = new Set<string>();
  map.entries.forEach((e: any, i: number) => {
    for (const key of REQUIRED) {
      if (!(key in e)) problems.push(`entry ${i} (${e.method ?? "?"}) missing ${key}`);
    }
    if (e.securityLevel && !SECURITY.has(e.securityLevel)) problems.push(`entry ${i} bad securityLevel ${e.securityLevel}`);
    if (e.mcpCoverage && !COVERAGE.has(e.mcpCoverage)) problems.push(`entry ${i} bad mcpCoverage ${e.mcpCoverage}`);
    if (e.testCoverage && !TESTCOV.has(e.testCoverage)) problems.push(`entry ${i} bad testCoverage ${e.testCoverage}`);
    if (e.securityLevel === "raw-exec" && e.mutatesScene !== true) {
      problems.push(`entry ${i} (${e.method}) raw-exec must mutate the scene`);
    }
    const key = `${e.namespace}::${e.method}::${e.signature}`;
    if (seen.has(key)) problems.push(`duplicate entry ${key}`);
    seen.add(key);
  });

  if (problems.length) {
    for (const p of problems) console.error("FAIL  %s", p);
    console.error("%d problem(s) in %d entries", problems.length, map.entries.length);
    return 1;
  }
  console.error("ok    %d capability entries valid (version %s%s)", map.entries.length, map.cavalryVersion ?? "?", map.partial ? ", partial" : "");
  return 0;
}

process.exit(main());
