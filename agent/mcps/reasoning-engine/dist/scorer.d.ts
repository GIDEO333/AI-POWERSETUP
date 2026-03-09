import type { CriteriaScores, Assumption, Attack, Contradiction } from './types.js';
/**
 * Compute weighted score E(A) from criteria scores, with a penalty if assumptions were killed.
 * Returns value between 0.0 and 1.0.
 */
export declare function computeScore(scores: CriteriaScores, survived: number, total: number): number;
/**
 * Detect contradictions between thesis assumptions and antithesis attacks.
 * Uses keyword overlap — no embeddings, no AI.
 */
export declare function detectContradictions(assumptions: Assumption[], attacks: Attack[]): Contradiction[];
/**
 * Count how many assumptions survived the antithesis attacks.
 * An assumption is "killed" if it has a fatal attack or multiple high attacks.
 */
export declare function countSurvivedAssumptions(assumptions: Assumption[], attacks: Attack[]): {
    survived: number;
    killed: number;
    total: number;
};
//# sourceMappingURL=scorer.d.ts.map