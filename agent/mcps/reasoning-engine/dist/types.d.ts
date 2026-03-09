/** The 4 phases of thesis-antithesis reasoning */
export type Phase = "thesis" | "antithesis" | "synthesis" | "stresstest";
/** Ordered phases for gate enforcement */
export declare const PHASE_ORDER: Phase[];
/** An explicit assumption stated during thesis */
export interface Assumption {
    id: string;
    text: string;
    survived?: boolean;
}
/** An attack on a specific assumption during antithesis */
export interface Attack {
    assumptionId: string;
    counterExample: string;
    severity: "low" | "medium" | "high" | "fatal";
}
/** Scores for the 4 evaluation criteria (0.0 – 1.0) */
export interface CriteriaScores {
    logicalConsistency: number;
    deductiveValidity: number;
    informationEfficiency: number;
    coherence: number;
}
/** A stress test scenario applied in the final phase */
export interface StressScenario {
    scenario: string;
    outcome: "pass" | "fail" | "partial";
    risk: "low" | "medium" | "high" | "critical";
    detail: string;
}
/** Detected contradiction between thesis assumption and antithesis attack */
export interface Contradiction {
    assumptionId: string;
    assumptionText: string;
    attackText: string;
    keywords: string[];
}
export interface ThesisAntithesisInput {
    phase: Phase;
    content: string;
    assumptions?: Assumption[];
    attacks?: Attack[];
    scores?: CriteriaScores;
    stressResults?: StressScenario[];
    premortem?: string;
    confidence?: number;
}
export interface ThesisAntithesisOutput {
    phase: Phase;
    phaseComplete: boolean;
    nextPhaseRequired: Phase | null;
    sessionId: string;
    phasesCompleted: Phase[];
    assumptionCount: number;
    assumptionsSurvived: number | null;
    contradictionsFound: Contradiction[];
    sessionScore: number | null;
    confidence: number | null;
    summary: string;
}
export interface SessionState {
    id: string;
    createdAt: number;
    currentPhase: Phase | null;
    phasesCompleted: Phase[];
    thesis: {
        content: string;
        assumptions: Assumption[];
    } | null;
    antithesis: {
        content: string;
        attacks: Attack[];
    } | null;
    synthesis: {
        content: string;
        scores: CriteriaScores | null;
        sessionScore: number | null;
    } | null;
    stresstest: {
        content: string;
        results: StressScenario[];
        premortem: string;
        confidence: number;
    } | null;
    contradictions: Contradiction[];
}
//# sourceMappingURL=types.d.ts.map