#!/usr/bin/env node
/**
 * Score one evaluation result against its scenario and expected graph.
 *
 * It fails closed: a result with no on-disk evidence, or with a block_if
 * condition this scorer does not recognise, cannot pass. It never fabricates a
 * metric — it reads result.metrics and result.evidence, which the run records.
 *
 * Usage:   node score-evaluation.ts <scenario.json> <result.json>
 * Exit:    0 PASS, 1 FAIL, 2 usage/IO error.
 *
 * Result shape:
 *   {
 *     "kind": "agent-run",
 *     "scenarioId": "01-...",
 *     "metrics": {
 *       "sourceGeometryCount": 1, "duplicatorCount": 1,
 *       "manuallyDuplicatedLayerCount": 0, "renders": 6,
 *       "distributionTypes": ["shapeEdgeDistribution"],
 *       "seamSampledWithClampedSetFrame": false,
 *       "duplicateTerminalFrame": false,
 *       "cornerPinDescribedAs3d": false,
 *       "cameraAttributeSetWithoutDiscovery": false,
 *       "attributeWrittenBeforeGetAttributes": false,
 *       "noReadbackAfterSet": false,
 *       "unknownPathReportedAsSuccess": false,
 *       "duplicatorCountAfterSecondRequest": 1
 *     },
 *     "evidence": { "tool_transcript": "...", "scene_graph": "...", "renders": "..." }
 *   }
 */

import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve, join } from "node:path";

type Check = { condition: string; blocked: boolean; recognised: boolean; detail: string };

function readJson(path: string): any {
  return JSON.parse(readFileSync(path, "utf8"));
}

function evalBlock(condition: string, m: Record<string, any>): Check {
  const c = condition.trim();
  const mk = (blocked: boolean, detail: string): Check => ({ condition: c, blocked, recognised: true, detail });

  if (/source_geometry_count\s*>=\s*3\s*and\s*duplicator_count\s*==\s*0/.test(c)) {
    const blocked = (m.sourceGeometryCount ?? 0) >= 3 && (m.duplicatorCount ?? 0) === 0;
    return mk(blocked, `sources=${m.sourceGeometryCount}, duplicators=${m.duplicatorCount}`);
  }
  if (/repeated_mark_count\s*>=\s*3\s*and\s*duplicator_count\s*==\s*0/.test(c)) {
    const blocked = (m.repeatedMarkCount ?? m.sourceGeometryCount ?? 0) >= 3 && (m.duplicatorCount ?? 0) === 0;
    return mk(blocked, `marks=${m.repeatedMarkCount ?? m.sourceGeometryCount}, duplicators=${m.duplicatorCount}`);
  }
  if (/render_count\s*<\s*6/.test(c)) {
    return mk((m.renders ?? 0) < 6, `renders=${m.renders}`);
  }
  if (/seam_sampled_with_clamped_setFrame/.test(c)) {
    return mk(m.seamSampledWithClampedSetFrame === true, `clampedSeam=${m.seamSampledWithClampedSetFrame}`);
  }
  if (/duplicator_count\s*>\s*1 after the second identical request/.test(c)) {
    return mk((m.duplicatorCountAfterSecondRequest ?? m.duplicatorCount ?? 0) > 1, `afterSecond=${m.duplicatorCountAfterSecondRequest}`);
  }
  if (/corner_pin_described_as_3d_geometry/.test(c)) {
    return mk(m.cornerPinDescribedAs3d === true, `cornerPinAs3d=${m.cornerPinDescribedAs3d}`);
  }
  if (/camera_attribute_set_without_discovery/.test(c)) {
    return mk(m.cameraAttributeSetWithoutDiscovery === true, `cameraNoDiscovery=${m.cameraAttributeSetWithoutDiscovery}`);
  }
  if (/attribute_written_before_getAttributes/.test(c)) {
    return mk(m.attributeWrittenBeforeGetAttributes === true, `writeBeforeList=${m.attributeWrittenBeforeGetAttributes}`);
  }
  if (/no_readback_after_set/.test(c)) {
    return mk(m.noReadbackAfterSet === true, `noReadback=${m.noReadbackAfterSet}`);
  }
  if (/unknown_path_reported_as_success/.test(c)) {
    return mk(m.unknownPathReportedAsSuccess === true, `unknownAsSuccess=${m.unknownPathReportedAsSuccess}`);
  }
  // Unrecognised condition — fail closed.
  return { condition: c, blocked: true, recognised: false, detail: "unrecognised condition; cannot score, failing closed" };
}

function main(): number {
  const [scenarioPath, resultPath] = process.argv.slice(2);
  if (!scenarioPath || !resultPath) {
    console.error("usage: score-evaluation.ts <scenario.json> <result.json>");
    return 2;
  }
  let scenario: any, result: any;
  try {
    scenario = readJson(scenarioPath);
  } catch (err) {
    console.error("cannot read scenario: %s", (err as Error).message);
    return 2;
  }
  try {
    result = readJson(resultPath);
  } catch (err) {
    console.error("cannot read result: %s", (err as Error).message);
    return 2;
  }

  const problems: string[] = [];

  // Evidence must exist on disk. No evidence, no pass.
  const resultDir = dirname(resolve(resultPath));
  const evidence = result.evidence || {};
  for (const key of ["tool_transcript", "scene_graph", "renders"]) {
    const rel = evidence[key];
    if (!rel) {
      problems.push(`missing evidence.${key}`);
      continue;
    }
    const abs = resolve(join(resultDir, rel));
    if (!existsSync(abs) && !existsSync(resolve(rel))) {
      problems.push(`evidence.${key} not found on disk: ${rel}`);
    }
  }
  if (result.kind !== "agent-run") problems.push(`result.kind must be "agent-run"`);
  if (result.scenarioId && scenario.id && result.scenarioId !== scenario.id) {
    problems.push(`scenarioId mismatch: ${result.scenarioId} vs ${scenario.id}`);
  }

  // Load the expected graph relative to the scenario.
  let expected: any = {};
  try {
    expected = readJson(resolve(join(dirname(resolve(scenarioPath)), "..", scenario.expected_graph)));
  } catch {
    try {
      expected = readJson(resolve(join(dirname(resolve(scenarioPath)), scenario.expected_graph)));
    } catch {
      problems.push("cannot load expected graph");
    }
  }

  const metrics = result.metrics || {};
  const checks: Check[] = (expected.block_if || []).map((c: string) => evalBlock(c, metrics));
  const blocked = checks.filter((c) => c.blocked);

  console.error("scenario %s — %s", scenario.id, scenario.title ?? "");
  for (const c of checks) {
    console.error("  %s  block_if: %s  [%s]", c.blocked ? "BLOCK" : "ok   ", c.condition, c.detail);
  }
  for (const p of problems) console.error("  FAIL  %s", p);

  if (problems.length || blocked.length) {
    console.error(
      "VERDICT FAIL — %d evidence/shape problem(s), %d block_if triggered",
      problems.length,
      blocked.length,
    );
    return 1;
  }
  console.error("VERDICT PASS — evidence present, no block_if triggered");
  return 0;
}

process.exit(main());
