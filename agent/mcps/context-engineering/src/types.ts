// ============================================================
// Context Engineering MCP — Type Definitions
// ============================================================

/** Urgency levels for GSD execution protocol */
export type Urgency = "low" | "medium" | "high" | "critical";

/** Domain lenses for BMAD analysis protocol */
export type Domain = "architecture" | "debugging" | "planning" | "research" | "review";

/** Analysis depth calibration */
export type Depth = "surface" | "deep" | "exhaustive";

// ---- GSD Types ----

export interface GsdInput {
  task: string;
  constraints?: string[];
  urgency: Urgency;
}

export interface GsdProtocol {
  mode: string;
  preflight: PreflightChecklist;
  executionDirectives: string[];
  antiPatterns: string[];
  taskTemplate: string;
  completionGate: string;
}

export interface PreflightChecklist {
  what: string;
  why: string;
  how: string;
}

// ---- BMAD Types ----

export interface BmadInput {
  objective: string;
  domain: Domain;
  depth: Depth;
  sessionContext?: string;
}

export interface BmadProtocol {
  domain: Domain;
  depth: Depth;
  phases: BmadPhase[];
  deliverable: string;
  sessionContinuity: string | null;
}

export interface BmadPhase {
  id: "B" | "M" | "A" | "D";
  name: string;
  description: string;
  questions: string[];
  outputs: string[];
}
