// ============================================================
// BMAD Framework — Structured Analysis Protocol Generator
// ============================================================
// Philosophy: Break → Map → Analyze → Deliver.
// Inspired by BMAD V6 (Breakthrough Method for Agile AI Development).
//
// Generates domain-specific analysis protocols with:
// - 5 domain lenses (architecture, debugging, planning, research, review)
// - 3 depth levels (surface, deep, exhaustive)
// - 4-phase B→M→A→D workflow per combination
// - Concrete deliverable specification
// - Session continuity for exhaustive depth

import type { BmadInput, BmadProtocol, BmadPhase, Domain, Depth } from './types.js';

// ---- Domain-Specific Question Banks ----

interface DomainLens {
  breakQuestions: string[];
  mapQuestions: string[];
  analyzeQuestions: string[];
  deliverable: string;
  breakOutputs: string[];
  mapOutputs: string[];
  analyzeOutputs: string[];
  deliverOutputs: string[];
}

const DOMAIN_LENSES: Record<Domain, DomainLens> = {
  architecture: {
    breakQuestions: [
      "What are the system boundaries? What's in scope vs out of scope?",
      "What are the core entities/concepts and their relationships?",
      "What quality attributes matter most? (performance, scalability, security, maintainability)",
      "What are the hard constraints? (tech stack, budget, timeline, team size)",
      "What existing systems must this integrate with?",
    ],
    mapQuestions: [
      "Draw the data flow: where does data enter, transform, and exit?",
      "What are the dependency relationships between components?",
      "Which components are stateful vs stateless?",
      "Where are the performance bottlenecks likely to emerge?",
      "What are the failure domains? If component X fails, what else breaks?",
    ],
    analyzeQuestions: [
      "Does this architecture satisfy all stated quality attributes?",
      "Where are the single points of failure?",
      "What's the scaling strategy for each component?",
      "Are there circular dependencies or tight coupling?",
      "What's the migration/evolution path if requirements change?",
      "What are the security boundaries and trust zones?",
    ],
    deliverable: "Architecture Decision Record (ADR) with: context, decision, consequences, alternatives considered.",
    breakOutputs: ["Component inventory", "Boundary diagram", "Constraint list"],
    mapOutputs: ["Dependency graph", "Data flow diagram", "Failure domain map"],
    analyzeOutputs: ["Quality attribute assessment", "Risk register", "Scaling strategy"],
    deliverOutputs: ["ADR document", "Component diagram", "API contracts"],
  },
  debugging: {
    breakQuestions: [
      "What is the exact observed behavior vs expected behavior?",
      "When did this start happening? What changed recently?",
      "Is it reproducible? Under what conditions?",
      "What's the scope of impact? (one user, all users, specific environment)",
      "Are there any error messages, logs, or stack traces?",
    ],
    mapQuestions: [
      "Trace the execution path: what code runs from trigger to failure?",
      "What external systems/APIs/services are involved in this path?",
      "What is the state of the system at the point of failure?",
      "Are there race conditions, timing dependencies, or ordering issues?",
      "What tests exist for this code path? Do they pass?",
    ],
    analyzeQuestions: [
      "List all hypotheses for the root cause, ranked by likelihood.",
      "For each hypothesis: what evidence supports it? What would disprove it?",
      "Is this a regression from a recent change, or a latent bug?",
      "Could this be a symptom of a deeper systemic issue?",
      "What's the minimal reproduction case?",
    ],
    deliverable: "Root Cause Analysis: root cause + evidence + fix plan + regression prevention.",
    breakOutputs: ["Bug report (observed vs expected)", "Impact assessment"],
    mapOutputs: ["Execution trace", "State snapshot at failure", "Dependency chain"],
    analyzeOutputs: ["Ranked hypothesis list", "Evidence matrix", "Minimal repro steps"],
    deliverOutputs: ["Root cause identification", "Fix implementation", "Regression test"],
  },
  planning: {
    breakQuestions: [
      "What is the end goal? How will we know it's achieved?",
      "What are the major milestones between now and done?",
      "What are the unknowns/risks that could derail the plan?",
      "Who are the stakeholders? What do they each need?",
      "What resources (time, people, budget) are available?",
    ],
    mapQuestions: [
      "What are the task dependencies? What must happen before what?",
      "Which tasks can be parallelized?",
      "Where are the critical path items that determine total timeline?",
      "What are the external dependencies (approvals, third-party deliveries)?",
      "What's the minimum viable deliverable at each milestone?",
    ],
    analyzeQuestions: [
      "Is the timeline realistic given the resources and dependencies?",
      "What's the biggest risk to the plan? What's the mitigation?",
      "Where can scope be cut if timeline pressure increases?",
      "Are there any unstated assumptions that could invalidate the plan?",
      "What's the rollback strategy if a milestone fails?",
    ],
    deliverable: "Project Plan: milestones, task breakdown, dependencies, timeline, risk register.",
    breakOutputs: ["Goal statement", "Milestone list", "Risk inventory"],
    mapOutputs: ["Task dependency graph", "Critical path analysis", "Resource allocation"],
    analyzeOutputs: ["Timeline feasibility assessment", "Risk mitigation strategies", "Scope flexibility analysis"],
    deliverOutputs: ["Detailed task plan", "Timeline with milestones", "Risk register with mitigations"],
  },
  research: {
    breakQuestions: [
      "What specific question(s) need answering?",
      "What would a 'good enough' answer look like?",
      "What domains/areas should be investigated?",
      "What existing knowledge do we already have?",
      "What are the boundaries of this research? When do we stop?",
    ],
    mapQuestions: [
      "What sources are available? (docs, repos, papers, experts)",
      "How do the research areas relate to each other?",
      "What's the credibility hierarchy of available sources?",
      "Are there conflicting viewpoints to reconcile?",
      "What prior art or existing solutions exist?",
    ],
    analyzeQuestions: [
      "What are the key findings across all sources?",
      "Where do sources agree? Where do they conflict?",
      "What gaps remain in our understanding?",
      "What are the practical implications of the findings?",
      "How confident are we in the conclusions? What would change them?",
    ],
    deliverable: "Research Report: findings summary, source analysis, recommendations, confidence levels.",
    breakOutputs: ["Research questions", "Scope definition", "Knowledge baseline"],
    mapOutputs: ["Source inventory", "Topic relationship map", "Prior art survey"],
    analyzeOutputs: ["Findings synthesis", "Conflict resolution", "Confidence assessment"],
    deliverOutputs: ["Research report", "Recommendations", "Next steps"],
  },
  review: {
    breakQuestions: [
      "What is being reviewed? (code, architecture, design, process)",
      "What are the review criteria? (correctness, security, performance, style)",
      "What's the scope? (specific files, entire module, system-wide)",
      "What's the risk profile? (public API, internal tool, critical path)",
      "Are there specific concerns or areas to focus on?",
    ],
    mapQuestions: [
      "What are the high-risk zones in the code/artifact under review?",
      "What are the dependencies of the reviewed component?",
      "Who will be affected by issues found? (users, other teams, systems)",
      "What tests or verification mechanisms exist?",
      "What's the change history? (recent changes, known issues)",
    ],
    analyzeQuestions: [
      "Does it meet all stated review criteria?",
      "Are there security vulnerabilities? (injection, auth bypass, data exposure)",
      "Are there performance issues? (N+1 queries, unnecessary computation, memory leaks)",
      "Is the code maintainable? (naming, structure, complexity, documentation)",
      "Are edge cases and error states handled?",
      "Does it follow established patterns and conventions?",
    ],
    deliverable: "Review Report: findings (critical/major/minor), action items, approval status.",
    breakOutputs: ["Review scope document", "Criteria checklist", "Risk assessment"],
    mapOutputs: ["Risk zone map", "Dependency analysis", "Change history"],
    analyzeOutputs: ["Findings list (categorized by severity)", "Pattern compliance check"],
    deliverOutputs: ["Review report", "Action items with owners", "Approval recommendation"],
  },
};

// ---- Depth Calibration ----

interface DepthConfig {
  label: string;
  timeEstimate: string;
  questionLimit: number;
  analysisScope: string;
  sessionHint: string;
}

const DEPTH_CONFIGS: Record<Depth, DepthConfig> = {
  surface: {
    label: "🔍 SURFACE SCAN — Quick assessment, broad strokes",
    timeEstimate: "15–30 minutes",
    questionLimit: 3,
    analysisScope: "Focus on the top 3 most important questions per phase. Skip edge cases.",
    sessionHint: "Complete in this session. No follow-up needed.",
  },
  deep: {
    label: "🔬 DEEP ANALYSIS — Thorough investigation, comprehensive coverage",
    timeEstimate: "1–2 hours",
    questionLimit: 5,
    analysisScope: "Address all questions per phase. Investigate edge cases and secondary concerns.",
    sessionHint: "Complete in this session with detailed output.",
  },
  exhaustive: {
    label: "🧬 EXHAUSTIVE — Multi-session, leave-no-stone-unturned investigation",
    timeEstimate: "Multiple sessions, potentially days",
    questionLimit: 999, // all questions
    analysisScope: "Address every question. Research external sources. Document all findings with evidence. Challenge every assumption.",
    sessionHint: "This will span multiple sessions. Save context for continuation.",
  },
};

// ---- Protocol Generator ----

export function generateBmadProtocol(input: BmadInput): BmadProtocol {
  const lens = DOMAIN_LENSES[input.domain];
  const depthCfg = DEPTH_CONFIGS[input.depth];
  const limit = depthCfg.questionLimit;

  const phases: BmadPhase[] = [
    {
      id: "B",
      name: "BREAK IT DOWN",
      description: `Decompose "${input.objective}" into its constituent parts. Identify boundaries, components, and constraints.`,
      questions: lens.breakQuestions.slice(0, limit),
      outputs: lens.breakOutputs,
    },
    {
      id: "M",
      name: "MAP DEPENDENCIES",
      description: `Map the relationships, dependencies, and flows between the components identified in Phase B.`,
      questions: lens.mapQuestions.slice(0, limit),
      outputs: lens.mapOutputs,
    },
    {
      id: "A",
      name: "ANALYZE DEEPLY",
      description: `Apply the ${input.domain} lens to analyze each component and relationship. ${depthCfg.analysisScope}`,
      questions: lens.analyzeQuestions.slice(0, limit),
      outputs: lens.analyzeOutputs,
    },
    {
      id: "D",
      name: "DELIVER PRECISELY",
      description: `Produce the concrete deliverable. Format: ${lens.deliverable}`,
      questions: [
        `Does the deliverable address the original objective: "${input.objective}"?`,
        "Are all findings backed by evidence from the analysis phase?",
        "Are action items specific, measurable, and assigned?",
      ],
      outputs: lens.deliverOutputs,
    },
  ];

  // Session continuity (only for exhaustive depth)
  let sessionContinuity: string | null = null;
  if (input.depth === "exhaustive") {
    sessionContinuity = input.sessionContext
      ? `CONTINUING FROM PREVIOUS SESSION:\n${input.sessionContext}\n\nResume from where the previous session left off. Review the context above and continue the analysis.`
      : `This is a new exhaustive session. At the end, save the following for the next session:\n1. Which phases are complete and which are pending\n2. Key findings so far\n3. Open questions that need further investigation\n4. Any hypotheses formed but not yet validated`;
  }

  return {
    domain: input.domain,
    depth: input.depth,
    phases,
    deliverable: lens.deliverable,
    sessionContinuity,
  };
}

// ---- Formatter ----

export function formatBmadProtocol(protocol: BmadProtocol, objective: string): string {
  const depthCfg = DEPTH_CONFIGS[protocol.depth];
  const lines: string[] = [];

  lines.push("═══════════════════════════════════════════════════════");
  lines.push("  BMAD ANALYSIS PROTOCOL — Break → Map → Analyze → Deliver");
  lines.push("═══════════════════════════════════════════════════════");
  lines.push("");
  lines.push(`  Objective: ${objective}`);
  lines.push(`  Domain: ${protocol.domain.toUpperCase()}`);
  lines.push(`  ${depthCfg.label}`);
  lines.push(`  Time estimate: ${depthCfg.timeEstimate}`);
  lines.push("");

  if (protocol.sessionContinuity) {
    lines.push("───────────────────────────────────────────────────────");
    lines.push("  📎 SESSION CONTINUITY");
    lines.push("───────────────────────────────────────────────────────");
    lines.push(`  ${protocol.sessionContinuity}`);
    lines.push("");
  }

  for (const phase of protocol.phases) {
    const phaseEmoji: Record<string, string> = {
      B: "🔨", M: "🗺️", A: "🔬", D: "📦",
    };

    lines.push("───────────────────────────────────────────────────────");
    lines.push(`  ${phaseEmoji[phase.id] ?? "•"} PHASE ${phase.id} — ${phase.name}`);
    lines.push("───────────────────────────────────────────────────────");
    lines.push(`  ${phase.description}`);
    lines.push("");
    lines.push("  Questions to answer:");
    for (let i = 0; i < phase.questions.length; i++) {
      lines.push(`    ${i + 1}. ${phase.questions[i]}`);
    }
    lines.push("");
    lines.push("  Expected outputs:");
    for (const output of phase.outputs) {
      lines.push(`    → ${output}`);
    }
    lines.push("");
  }

  lines.push("───────────────────────────────────────────────────────");
  lines.push("  🎯 DELIVERABLE SPECIFICATION");
  lines.push("───────────────────────────────────────────────────────");
  lines.push(`  ${protocol.deliverable}`);
  lines.push("");
  lines.push(`  ${depthCfg.sessionHint}`);
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════");
  lines.push("  Inspired by BMAD methodology (github.com/bmad-code-org/BMAD-METHOD)");
  lines.push("  For the full framework: npx bmad-method install");
  lines.push("═══════════════════════════════════════════════════════");

  return lines.join("\n");
}
