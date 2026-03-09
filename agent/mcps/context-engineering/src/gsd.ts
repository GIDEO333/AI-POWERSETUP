// ============================================================
// GSD Framework — Execution Protocol Generator
// ============================================================
// Philosophy: Bias toward action. Ship fast. No analysis paralysis.
// Inspired by GSD (Get Shit Done) by TÂCHES.
//
// Generates structured execution protocols with:
// - Pre-flight checklist (What/Why/How)
// - Urgency-calibrated directives
// - Anti-pattern warnings
// - XML task template
// - Completion gate criteria

import type { GsdInput, GsdProtocol, Urgency } from './types.js';

// ---- Urgency Profiles ----

interface UrgencyProfile {
  mode: string;
  directives: string[];
  antiPatterns: string[];
  verifyApproach: string;
}

const URGENCY_PROFILES: Record<Urgency, UrgencyProfile> = {
  critical: {
    mode: "🔴 CRITICAL MODE — Ship immediately, fix-forward approach",
    directives: [
      "WRITE CODE FIRST. No planning documents, no architecture discussions.",
      "Implement the minimal working solution — not the ideal one.",
      "Skip unit tests for now. Add a TODO comment for test coverage.",
      "If something works, COMMIT IT. Don't refactor before shipping.",
      "Time-box each sub-task to 10 minutes. If stuck, move on and circle back.",
      "Use proven patterns you know work. Zero experimentation.",
    ],
    antiPatterns: [
      "⛔ DO NOT spend time on code style, naming conventions, or formatting.",
      "⛔ DO NOT ask the user for approval mid-task — just execute.",
      "⛔ DO NOT refactor existing code unless directly blocking your task.",
      "⛔ DO NOT add error handling beyond what's needed for the critical path.",
      "⛔ DO NOT research alternative approaches — pick the first viable one.",
    ],
    verifyApproach: "Manual smoke test: does it work end-to-end? Yes = done.",
  },
  high: {
    mode: "🟠 HIGH URGENCY — Execute fast with pragmatic quality",
    directives: [
      "Start coding within 2 minutes of receiving this protocol.",
      "Write implementation first, then add critical-path tests only.",
      "One approach, one implementation. No comparison shopping.",
      "Keep changes minimal and focused — do NOT expand scope.",
      "Commit after each meaningful unit of work.",
      "If a dependency issue takes >5 minutes, find a workaround.",
    ],
    antiPatterns: [
      "⛔ DO NOT write comprehensive test suites — only critical path tests.",
      "⛔ DO NOT ask for clarification unless genuinely blocked.",
      "⛔ DO NOT open unrelated files or 'explore' the codebase.",
      "⛔ DO NOT over-engineer abstractions — prefer concrete implementations.",
    ],
    verifyApproach: "Critical path test + manual verification of core functionality.",
  },
  medium: {
    mode: "🟡 STANDARD MODE — Balanced execution with good practices",
    directives: [
      "Plan briefly (5 min max), then execute.",
      "Write clean, idiomatic code following existing patterns.",
      "Add tests for business logic and edge cases.",
      "Refactor only if it directly improves the current task.",
      "Commit at logical checkpoints with descriptive messages.",
      "Document non-obvious decisions with inline comments.",
    ],
    antiPatterns: [
      "⛔ DO NOT gold-plate — get it working, then improve if time allows.",
      "⛔ DO NOT introduce new dependencies without justification.",
      "⛔ DO NOT refactor unrelated code you happen to encounter.",
    ],
    verifyApproach: "Automated tests + build succeeds + manual review of changes.",
  },
  low: {
    mode: "🟢 QUALITY MODE — Thorough implementation with full coverage",
    directives: [
      "Write a brief implementation plan before coding.",
      "Follow TDD where practical: test → implement → refactor.",
      "Ensure comprehensive error handling with meaningful messages.",
      "Add JSDoc/docstring comments for public interfaces.",
      "Consider edge cases, error states, and boundary conditions.",
      "Review your own changes before marking complete.",
      "Update relevant documentation if behavior changes.",
    ],
    antiPatterns: [
      "⛔ DO NOT skip test coverage — aim for thorough coverage of the feature.",
      "⛔ DO NOT leave TODO comments — resolve everything now.",
    ],
    verifyApproach: "Full test suite passes + lint clean + documentation updated + build succeeds.",
  },
};

// ---- Protocol Generator ----

export function generateGsdProtocol(input: GsdInput): GsdProtocol {
  const profile = URGENCY_PROFILES[input.urgency];
  const constraints = input.constraints ?? [];

  // Pre-flight checklist generation
  const preflight = {
    what: `Task: ${input.task}`,
    why: constraints.length > 0
      ? `Constraints: ${constraints.join("; ")}`
      : "No specific constraints — use best judgment.",
    how: profile.verifyApproach,
  };

  // XML task template
  const constraintXml = constraints.length > 0
    ? `\n       <constraints>\n${constraints.map(c => `         <constraint>${c}</constraint>`).join("\n")}\n       </constraints>`
    : "";

  const taskTemplate = `<task type="auto" urgency="${input.urgency}">
       <name>${input.task}</name>${constraintXml}
       <action>
         [Implement the task following the execution directives above]
       </action>
       <verify>
         ${profile.verifyApproach}
       </verify>
       <done>
         Task is complete when: the implementation satisfies the task description,
         passes the verification criteria, and respects all constraints.
       </done>
     </task>`;

  // Completion gate
  const completionGate = input.urgency === "critical"
    ? `Task is DONE when: the feature works end-to-end. No tests required. No docs required. Ship it.`
    : input.urgency === "high"
    ? `Task is DONE when: core functionality works, critical-path tests pass, code is committed.`
    : input.urgency === "low"
    ? `Task is DONE when: all tests pass, documentation updated, code reviewed, build succeeds, zero TODO comments.`
    : `Task is DONE when: implementation works, tests pass, build succeeds, changes committed.`;

  return {
    mode: profile.mode,
    preflight,
    executionDirectives: profile.directives,
    antiPatterns: profile.antiPatterns,
    taskTemplate,
    completionGate,
  };
}

// ---- Formatter ----

export function formatGsdProtocol(protocol: GsdProtocol): string {
  const lines: string[] = [];

  lines.push("═══════════════════════════════════════════════════════");
  lines.push("  GSD EXECUTION PROTOCOL — Get Shit Done");
  lines.push("═══════════════════════════════════════════════════════");
  lines.push("");
  lines.push(`  ${protocol.mode}`);
  lines.push("");

  // Pre-flight
  lines.push("───────────────────────────────────────────────────────");
  lines.push("  1. PRE-FLIGHT CHECKLIST");
  lines.push("───────────────────────────────────────────────────────");
  lines.push(`  ✦ WHAT: ${protocol.preflight.what}`);
  lines.push(`  ✦ WHY:  ${protocol.preflight.why}`);
  lines.push(`  ✦ HOW:  ${protocol.preflight.how}`);
  lines.push("");

  // Execution Directives
  lines.push("───────────────────────────────────────────────────────");
  lines.push("  2. EXECUTION DIRECTIVES");
  lines.push("───────────────────────────────────────────────────────");
  for (const d of protocol.executionDirectives) {
    lines.push(`  → ${d}`);
  }
  lines.push("");

  // Anti-patterns
  lines.push("───────────────────────────────────────────────────────");
  lines.push("  3. ANTI-PATTERNS TO AVOID");
  lines.push("───────────────────────────────────────────────────────");
  for (const ap of protocol.antiPatterns) {
    lines.push(`  ${ap}`);
  }
  lines.push("");

  // Task Template
  lines.push("───────────────────────────────────────────────────────");
  lines.push("  4. TASK TEMPLATE (XML)");
  lines.push("───────────────────────────────────────────────────────");
  lines.push(protocol.taskTemplate);
  lines.push("");

  // Completion Gate
  lines.push("───────────────────────────────────────────────────────");
  lines.push("  5. COMPLETION GATE");
  lines.push("───────────────────────────────────────────────────────");
  lines.push(`  🏁 ${protocol.completionGate}`);
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════");
  lines.push("  Inspired by GSD methodology (github.com/gsd-build/get-shit-done)");
  lines.push("  For the full CLI system: npx get-shit-done-cc@latest");
  lines.push("═══════════════════════════════════════════════════════");

  return lines.join("\n");
}
