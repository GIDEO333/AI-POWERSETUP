#!/usr/bin/env node
// ============================================================
// Reasoning Engine MCP Server
// ============================================================
// Unified thinking toolkit for AI agents.
// 
// 2 tools:
//   1. sequentialthinking — Linear step-by-step reasoning with branching
//   2. thesis-antithesis  — Adversarial 4-phase reasoning with scoring
//
// Zero API keys. Zero external dependencies. Pure logic.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { ThesisAntithesisEngine } from './engine.js';
import { SequentialThinkingServer } from './sequential.js';

const server = new McpServer({
  name: "reasoning-engine",
  version: "1.0.0",
});

const thesisEngine = new ThesisAntithesisEngine();
const sequentialServer = new SequentialThinkingServer();

// ================================================================
// TOOL 1: Sequential Thinking
// (Ported from @modelcontextprotocol/server-sequential-thinking)
// ================================================================

server.registerTool("sequentialthinking", {
  title: "Sequential Thinking",
  description: `A detailed tool for dynamic and reflective problem-solving through thoughts.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Problems that require a multi-step solution
- Analysis that might need course correction

Do NOT use for evaluating decisions or trade-offs between options — use thesis-antithesis-thinking instead.

Only set nextThoughtNeeded to false when truly done and a satisfactory answer is reached.`,
  inputSchema: {
    thought: z.string().describe("Your current thinking step"),
    nextThoughtNeeded: z.boolean().describe("Whether another thought step is needed"),
    thoughtNumber: z.number().int().min(1).describe("Current thought number (numeric value, e.g., 1, 2, 3)"),
    totalThoughts: z.number().int().min(1).describe("Estimated total thoughts needed (numeric value, e.g., 5, 10)"),
    isRevision: z.boolean().optional().describe("Whether this revises previous thinking"),
    revisesThought: z.number().int().min(1).optional().describe("Which thought is being reconsidered"),
    branchFromThought: z.number().int().min(1).optional().describe("Branching point thought number"),
    branchId: z.string().optional().describe("Branch identifier"),
    needsMoreThoughts: z.boolean().optional().describe("If more thoughts are needed"),
  },
}, async (args) => {
  const result = sequentialServer.processThought(args);
  return {
    content: [{
      type: "text",
      text: JSON.stringify(result, null, 2),
    }],
  };
});

// ================================================================
// TOOL 2: Thesis-Antithesis Thinking
// ================================================================

const AssumptionSchema = z.object({
  id: z.string().describe("Unique ID for the assumption, e.g. 'A1', 'A2'"),
  text: z.string().describe("The assumption statement"),
});

const AttackSchema = z.object({
  assumptionId: z.string().describe("ID of the assumption being attacked"),
  counterExample: z.string().describe("Counter-example that challenges the assumption"),
  severity: z.enum(["low", "medium", "high", "fatal"]).describe("How damaging this attack is"),
});

const CriteriaScoresSchema = z.object({
  logicalConsistency: z.number().min(0).max(1).describe("C: free from internal contradictions (0-1)"),
  deductiveValidity: z.number().min(0).max(1).describe("V: conclusions follow from premises (0-1)"),
  informationEfficiency: z.number().min(0).max(1).describe("I: dense info, no redundancy (0-1)"),
  coherence: z.number().min(0).max(1).describe("K: flows logically, no jumps (0-1)"),
});

const StressScenarioSchema = z.object({
  scenario: z.string().describe("Edge case or failure scenario description"),
  outcome: z.enum(["pass", "fail", "partial"]).describe("Did the solution handle it?"),
  risk: z.enum(["low", "medium", "high", "critical"]).describe("Risk level if this scenario materializes"),
  detail: z.string().describe("Specific outcome detail"),
});

server.registerTool("thesis-antithesis-thinking", {
  title: "Thesis-Antithesis Thinking",
  description: `Adversarial reasoning through 4 phases with server-enforced ordering and scoring.
Phases: thesis → antithesis → synthesis → stresstest. Server enforces order.

PHASE 1 — THESIS: State your solution and list EXPLICIT assumptions.
PHASE 2 — ANTITHESIS: Attack EVERY assumption with counter-examples. Server detects contradictions.
PHASE 3 — SYNTHESIS: Score thesis vs antithesis on 4 criteria. Server computes E(A).
PHASE 4 — STRESSTEST: Apply edge cases and pre-mortem. Provide final confidence.

Use for: architecture decisions, trade-off analysis, debugging hypotheses, any decision needing rigor.
Do NOT use for step-by-step problem solving or implementation planning — use sequentialthinking instead.`,

  inputSchema: {
    phase: z.enum(["thesis", "antithesis", "synthesis", "stresstest"])
      .describe("Current thesis-antithesis phase. Server enforces ordering."),
    content: z.string()
      .describe("Your reasoning for this phase"),
    assumptions: z.array(AssumptionSchema).optional()
      .describe("Phase 1 (thesis): list of explicit assumptions with unique IDs"),
    attacks: z.array(AttackSchema).optional()
      .describe("Phase 2 (antithesis): attacks on specific assumptions by ID"),
    scores: CriteriaScoresSchema.optional()
      .describe("Phase 3 (synthesis): score the overall reasoning on 4 criteria (0-1 each)"),
    stressResults: z.array(StressScenarioSchema).optional()
      .describe("Phase 4 (stresstest): edge case test results"),
    premortem: z.string().optional()
      .describe("Phase 4: 'How does this fail in 6 months?' narrative"),
    confidence: z.number().min(0).max(1).optional()
      .describe("Phase 4: final confidence score (0-1)"),
  },
}, async (args) => {
  const result = thesisEngine.processPhase(args);

  const lines: string[] = [];
  const s = result;

  if (s.summary.startsWith("ERROR:")) {
    lines.push(`❌ ${s.summary}`);
    return {
      content: [{ type: "text", text: lines.join('\n') }],
      isError: true,
    };
  }

  const phaseEmoji: Record<string, string> = {
    thesis: "📜", antithesis: "⚔️", synthesis: "🔀", stresstest: "🔥"
  };
  lines.push(`${phaseEmoji[s.phase] ?? '•'} Phase: ${s.phase.toUpperCase()} — Complete`);
  lines.push(`📋 Session: ${s.sessionId}`);
  lines.push(`✅ Phases done: [${s.phasesCompleted.join(' → ')}]`);

  if (s.assumptionCount > 0) {
    lines.push(`📌 Assumptions: ${s.assumptionCount}`);
  }
  if (s.assumptionsSurvived !== null) {
    lines.push(`🛡️ Survived: ${s.assumptionsSurvived}/${s.assumptionCount}`);
  }
  if (s.contradictionsFound.length > 0) {
    lines.push(`⚠️ Contradictions: ${s.contradictionsFound.length}`);
    for (const c of s.contradictionsFound) {
      lines.push(`   [${c.assumptionId}] "${c.assumptionText}" vs "${c.attackText}" (keywords: ${c.keywords.join(', ')})`);
    }
  }
  if (s.sessionScore !== null) {
    lines.push(`📊 E(A) Score: ${s.sessionScore}`);
  }
  if (s.confidence !== null) {
    lines.push(`🎯 Confidence: ${(s.confidence * 100).toFixed(0)}%`);
  }

  if (s.nextPhaseRequired) {
    lines.push(`\n➡️ Next: call thesis-antithesis-thinking with phase="${s.nextPhaseRequired}"`);
  } else {
    lines.push(`\n✅ Thesis-Antithesis Thinking complete. Session finished.`);
  }

  lines.push(`\n💬 ${s.summary}`);

  return {
    content: [{ type: "text", text: lines.join('\n') }],
  };
});

// ---- Run ----

async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("🧠 Reasoning Engine MCP Server running on stdio (2 tools: sequentialthinking, thesis-antithesis-thinking)");
}

runServer().catch((error) => {
  console.error("Fatal error running server:", error);
  process.exit(1);
});
