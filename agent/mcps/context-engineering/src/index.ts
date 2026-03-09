#!/usr/bin/env node
// ============================================================
// Context Engineering MCP Server
// ============================================================
// On-demand context engineering protocols for AI agents.
//
// 2 tools:
//   1. gsd-framework  — Execution protocol (Get Shit Done mode)
//   2. bmad-framework — Analysis protocol (Break → Map → Analyze → Deliver)
//
// Zero API keys. Zero external dependencies. Pure logic.
// Inspired by GSD (github.com/gsd-build/get-shit-done)
// and BMAD V6 (github.com/bmad-code-org/BMAD-METHOD).

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { generateGsdProtocol, formatGsdProtocol } from './gsd.js';
import { generateBmadProtocol, formatBmadProtocol } from './bmad.js';

const server = new McpServer({
  name: "context-engineering",
  version: "1.0.0",
});

// ================================================================
// TOOL 1: GSD Framework — Execution Protocol Generator
// ================================================================

server.registerTool("gsd-framework", {
  title: "GSD Framework",
  description: `Activates GSD (Get Shit Done) mode — generates a structured execution protocol.
Use when: task is clear, execution is priority, no room for analysis paralysis.
Returns: pre-flight checklist, urgency-calibrated directives, anti-patterns, XML task template, completion gate.
Do NOT use for: architecture decisions, complex trade-offs, or deep analysis — use bmad-framework instead.`,
  inputSchema: {
    task: z.string().describe("Description of the task to execute"),
    constraints: z.array(z.string()).optional()
      .describe("Constraints that must be respected during execution"),
    urgency: z.enum(["low", "medium", "high", "critical"]).default("medium")
      .describe("Urgency level: low=quality focus, medium=balanced, high=speed priority, critical=ship immediately"),
  },
}, async (args) => {
  const protocol = generateGsdProtocol({
    task: args.task,
    constraints: args.constraints,
    urgency: args.urgency,
  });

  return {
    content: [{
      type: "text",
      text: formatGsdProtocol(protocol),
    }],
  };
});

// ================================================================
// TOOL 2: BMAD Framework — Analysis Protocol Generator
// ================================================================

server.registerTool("bmad-framework", {
  title: "BMAD Framework",
  description: `Activates BMAD V6 structured thinking mode: Break → Map → Analyze → Deliver.
Use when: complex objective, multi-step planning, architecture decisions, deep debugging, or thorough review needed.
Returns: domain-specific 4-phase analysis protocol with calibrated depth, question trees, and deliverable specification.
5 domains: architecture, debugging, planning, research, review.
3 depths: surface (15 min), deep (1-2 hours), exhaustive (multi-session).
Do NOT use for: simple tasks with obvious execution path — use gsd-framework instead.`,
  inputSchema: {
    objective: z.string().describe("High-level objective to analyze"),
    domain: z.enum(["architecture", "debugging", "planning", "research", "review"])
      .describe("Domain lens to apply — determines question types and deliverable format"),
    depth: z.enum(["surface", "deep", "exhaustive"]).default("deep")
      .describe("Analysis depth: surface=quick scan, deep=thorough, exhaustive=multi-session"),
    sessionContext: z.string().optional()
      .describe("Context from a previous exhaustive session to continue from"),
  },
}, async (args) => {
  const protocol = generateBmadProtocol({
    objective: args.objective,
    domain: args.domain,
    depth: args.depth,
    sessionContext: args.sessionContext,
  });

  return {
    content: [{
      type: "text",
      text: formatBmadProtocol(protocol, args.objective),
    }],
  };
});

// ---- Run ----

async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("🎯 Context Engineering MCP running (2 tools: gsd-framework, bmad-framework)");
}

runServer().catch((error) => {
  console.error("Fatal error running server:", error);
  process.exit(1);
});
