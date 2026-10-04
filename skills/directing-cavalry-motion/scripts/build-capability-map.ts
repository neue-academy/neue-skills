#!/usr/bin/env node
/**
 * Generate a machine-readable Cavalry MCP capability map from the installed
 * Cavalry type definitions and API metadata — never hand-maintained.
 *
 * It reads, when present:
 *   <Cavalry.app>/Contents/assets/MetaData/*.json   (JS API surface)
 *   <Cavalry.app>/Contents/assets/Definitions/nodeDefinitions.json (layer types)
 * and the installed MCP extension's manifest for the forwarded tool list.
 *
 * It never invents entries. When a source is missing it marks the whole map
 * `partial: true` and records which sources were unreadable, so a consumer can
 * tell "no data" from "zero capabilities".
 *
 * Usage:
 *   node build-capability-map.ts [--app <Cavalry.app>] [--out <file>]
 * Exit: 0 on success, 2 on usage/IO error.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

type Entry = {
  namespace: string;
  method: string;
  signature: string;
  category: string;
  returnType: string;
  mutatesScene: boolean | "unknown";
  securityLevel: "read" | "mutate" | "raw-exec" | "unknown";
  mcpCoverage: "direct-tool" | "via-execute_script" | "none";
  versionVerified: string;
  testCoverage: "none" | "fixture" | "live";
  limitations: string;
  sourceUrl: string;
};

const DOCS = "https://cavalry.studio/help/";

function arg(flag: string): string | undefined {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

function defaultApp(): string {
  for (const p of ["/Applications/Cavalry.app", join(process.env.HOME || "", "Applications/Cavalry.app")]) {
    if (existsSync(p)) return p;
  }
  return "/Applications/Cavalry.app";
}

function readJson(path: string): unknown | null {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return null;
  }
}

function appVersion(app: string): string {
  const info = join(app, "Contents/Info.plist");
  try {
    const text = readFileSync(info, "utf8");
    const m = text.match(/<key>CFBundleShortVersionString<\/key>\s*<string>([^<]+)<\/string>/);
    return m ? m[1] : "unknown";
  } catch {
    return "unknown";
  }
}

const MUTATING_HINTS = ["create", "set", "connect", "delete", "parent", "rename", "add", "remove", "install", "write", "duplicate", "keyframe", "setGenerator", "setFrame", "setEditablePath"];

function categorise(namespace: string, name: string): string {
  if (namespace.includes("GUI")) return "scene-mutation";
  if (/^get|^search|^read|^list|Bounding|Attributes|Selection|Children/i.test(name)) return "introspection";
  return "utility";
}

function mutates(name: string): boolean {
  return MUTATING_HINTS.some((h) => name.toLowerCase().startsWith(h.toLowerCase()));
}

function main(): number {
  const app = arg("--app") || defaultApp();
  const out = arg("--out") || join(process.cwd(), "references/mcp-capability-map.json");
  const version = appVersion(app);
  const missing: string[] = [];
  const entries: Entry[] = [];

  // 1. Forwarded MCP tools, from the installed extension manifest.
  const extManifest =
    readJson(join(process.env.HOME || "", "Library/Application Support/Claude/Claude Extensions/cavalry-mcp-server/manifest.json")) as
      | { tools?: { name: string; description?: string }[] }
      | null;
  if (extManifest?.tools) {
    for (const t of extManifest.tools) {
      const raw = t.name === "execute_script";
      entries.push({
        namespace: "mcp",
        method: t.name,
        signature: t.name + "(...)",
        category: "mcp-tool",
        returnType: t.name === "snapshot_layer" ? "image/png" : "text",
        mutatesScene: raw || t.name === "save_script_to_library" || t.name === "cleanup_workspace",
        securityLevel: raw ? "raw-exec" : "read",
        mcpCoverage: "direct-tool",
        versionVerified: "extension 1.0.0",
        testCoverage: "none",
        limitations: t.description ? t.description.slice(0, 160) : "",
        sourceUrl: "https://cavalry.studio/help/ai-connector-setup/",
      });
    }
  } else {
    missing.push("extension manifest.json");
  }

  // 2. JS API surface, from MetaData/*.json.
  const metaDir = join(app, "Contents/assets/MetaData");
  if (existsSync(metaDir)) {
    for (const file of readdirSync(metaDir).filter((f) => f.endsWith(".json"))) {
      const arr = readJson(join(metaDir, file)) as
        | { name: string; arguments?: { name: string; type?: string }[]; return_type?: string; namespace?: string; type?: string }[]
        | null;
      if (!Array.isArray(arr)) continue;
      for (const fn of arr) {
        const ns = fn.namespace || "api";
        const sig =
          fn.name +
          "(" +
          (fn.arguments || []).map((a) => `${a.name}: ${a.type || "any"}`).join(", ") +
          ")";
        entries.push({
          namespace: ns,
          method: fn.name,
          signature: sig,
          category: categorise(ns, fn.name),
          returnType: fn.return_type || "void",
          mutatesScene: mutates(fn.name),
          securityLevel: mutates(fn.name) ? "mutate" : "read",
          mcpCoverage: "via-execute_script",
          versionVerified: version,
          testCoverage: "none",
          limitations: "",
          sourceUrl: DOCS,
        });
      }
    }
  } else {
    missing.push("MetaData/*.json");
  }

  // 3. Layer-type count, from nodeDefinitions.json (recorded as a summary entry).
  const defs = readJson(join(app, "Contents/assets/Definitions/nodeDefinitions.json")) as
    | { nodeType?: string; abstract?: boolean; hide?: boolean }[]
    | null;
  let typeSummary: Record<string, number> | null = null;
  if (Array.isArray(defs)) {
    const creatable = defs.filter((d) => d.nodeType && !d.abstract && !d.hide);
    typeSummary = { total: defs.length, creatableCandidates: creatable.length };
  } else {
    missing.push("nodeDefinitions.json");
  }

  const map = {
    generatedBy: "build-capability-map.ts",
    note: "Generated from installed Cavalry assets. Entries describe the surface, not proof a call succeeds; testCoverage stays 'none' until a live run records otherwise.",
    cavalryVersion: version,
    partial: missing.length > 0,
    missingSources: missing,
    layerTypeSummary: typeSummary,
    entryCount: entries.length,
    entries,
  };

  try {
    writeFileSync(out, JSON.stringify(map, null, 2) + "\n");
  } catch (err) {
    console.error("build-capability-map: cannot write %s: %s", out, (err as Error).message);
    return 2;
  }
  console.error(
    "build-capability-map: wrote %d entries to %s (version %s%s)",
    entries.length,
    out,
    version,
    missing.length ? `, partial — missing: ${missing.join(", ")}` : "",
  );
  return 0;
}

process.exit(main());
