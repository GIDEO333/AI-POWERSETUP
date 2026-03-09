import type { ThesisAntithesisInput, ThesisAntithesisOutput } from './types.js';
export declare class ThesisAntithesisEngine {
    private sessions;
    /**
     * Process a thesis-antithesis tool call.
     * Enforces phase ordering, stores state, computes scores.
     */
    processPhase(input: ThesisAntithesisInput): ThesisAntithesisOutput;
    /**
     * Reset all sessions (useful for testing).
     */
    reset(): void;
    private getOrCreateSession;
    private checkPhaseGate;
    private buildSummary;
    private errorOutput;
    private generateId;
}
//# sourceMappingURL=engine.d.ts.map