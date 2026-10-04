#!/usr/bin/env node
/**
 * Validate a graph plan against the schema's required fields and the skill's
 * procedural decision rules. This is the gate that blocks the independent-shapes
 * anti-pattern BEFORE any Cavalry construction.
 *
 * Usage:   node validate-scene-graph.ts <plan.json>
 * Exit:    0 valid, 1 violates a rule, 2 usage/IO error.
 */

import { readFileSync } from "node:fs";

const REQUIRED = [
  "sourceGeometry",
  "proceduralSystems",
  "generatorsAndDistributions",
  "expectedConnections",
  "controllerAttributes",
  "animationDuration",
  "loopStrategy",
  "verificationFrames",
  "assumptions",
  "rollbackPoint",
] as const;

const LAYOUT_TO_DISTRIBUTION: Record<string, string[]> = {
  linear: ["linearDistribution"],
  grid: ["gridDistribution"],
  circle: ["circleDistribution"],
  "shape-edges": ["shapeEdgeDistribution"],
  "shape-points": ["shapePointDistribution"],
  random: ["randomDistribution"],
  custom: ["customDistribution"],
  path: ["pathDistribution", "shapeEdgeDistribution"],
};

const LOOP_FRAMES = ["0%", "25%", "50%", "75%", "final", "seam-adjacent"];

function main(): number {
  const path = process.argv[2];
  if (!path) {
    console.error("usage: validate-scene-graph.ts <plan.json>");
    return 2;
  }
  let plan: any;
  try {
    plan = JSON.parse(readFileSync(path, "utf8"));
  } catch (err) {
    console.error("cannot read %s: %s", path, (err as Error).message);
    return 2;
  }

  const problems: string[] = [];
  for (const key of REQUIRED) {
    if (!(key in plan)) problems.push(`missing required field: ${key}`);
  }
  if (problems.length) {
    for (const p of problems) console.error("FAIL  %s", p);
    return 1;
  }

  const sources = Array.isArray(plan.sourceGeometry) ? plan.sourceGeometry : [];
  const systems = Array.isArray(plan.proceduralSystems) ? plan.proceduralSystems : [];
  const dists = Array.isArray(plan.generatorsAndDistributions) ? plan.generatorsAndDistributions : [];
  const duplicators = systems.filter((s: any) => s.kind === "duplicator");

  // Rule 1 — the anti-pattern this skill exists to stop.
  if (sources.length >= 3 && duplicators.length === 0) {
    problems.push(
      `${sources.length} source shapes with no duplicator. Three or more repeated objects must be one source plus a Duplicator.`,
    );
  }

  // Rule 2 — a declared layout must use the distribution that describes it.
  for (const d of dists) {
    const allowed = LAYOUT_TO_DISTRIBUTION[d.layout];
    if (allowed && d.catalogNodeType && !allowed.includes(d.catalogNodeType)) {
      problems.push(
        `distribution "${d.alias ?? d.catalogNodeType}" declares layout ${d.layout} but type ${d.catalogNodeType}; expected one of ${allowed.join(", ")}`,
      );
    }
    if (d.layout === "random") {
      // seed must be a controller attribute for reproducibility
      const hasSeed = (plan.controllerAttributes || []).some((c: any) => /seed/i.test(c.attribute || ""));
      if (!hasSeed) problems.push(`random layout "${d.alias}" needs an explicit seed in controllerAttributes`);
    }
  }

  // Rule 3 — a duplicator needs a source and a distribution wired in.
  for (const dup of duplicators) {
    const feedsSource = (plan.expectedConnections || []).some((c: any) => (c.to || "").startsWith(`${dup.alias}.shapes`));
    const hasGenerator = (plan.expectedConnections || []).some((c: any) => (c.to || "").startsWith(`${dup.alias}.generator`)) ||
      dists.length > 0;
    if (!feedsSource) problems.push(`duplicator "${dup.alias}" has no source wired into .shapes`);
    if (!hasGenerator) problems.push(`duplicator "${dup.alias}" has no distribution in .generator`);
  }

  // Rule 4 — a loop must verify the full frame set.
  if (plan.loopStrategy?.loops === true) {
    const frames = (plan.verificationFrames || []).map(String);
    for (const f of LOOP_FRAMES) {
      if (!frames.includes(f)) problems.push(`loop plan missing verification frame: ${f}`);
    }
    if (plan.loopStrategy.endFrameRule && !/n\s*-\s*1/i.test(plan.loopStrategy.endFrameRule)) {
      problems.push(`loop endFrameRule should encode endFrame = N - 1`);
    }
  }

  // Rule 5 — unverified ids must be declared as assumptions, not silently trusted.
  const unverified = [...sources, ...systems, ...dists].filter((n: any) => n.runtimeVerified === false);
  if (unverified.length > 0 && (plan.assumptions || []).length === 0) {
    problems.push(`${unverified.length} node(s) are runtimeVerified:false but assumptions is empty — list them`);
  }

  // Rule 6 — a rollback point must be captured before building.
  if (plan.rollbackPoint?.capturedBefore !== true) {
    problems.push(`rollbackPoint.capturedBefore must be true before construction`);
  }

  if (problems.length) {
    for (const p of problems) console.error("FAIL  %s", p);
    console.error("%d rule violation(s)", problems.length);
    return 1;
  }
  console.error(
    "ok    graph plan valid: %d source, %d duplicator(s), %d distribution(s)%s",
    sources.length,
    duplicators.length,
    dists.length,
    plan.loopStrategy?.loops ? ", loop frames complete" : "",
  );
  return 0;
}

process.exit(main());
