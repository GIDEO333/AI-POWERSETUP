// ============================================================
// Thesis-Antithesis Engine — Scoring Module
// ============================================================
// Computes E(A) = 0.30·C + 0.25·V + 0.25·I + 0.20·K
// All scoring is arithmetic — ZERO AI, ZERO API calls.
/** Scoring weights */
const WEIGHTS = {
    logicalConsistency: 0.30, // C
    deductiveValidity: 0.25, // V
    informationEfficiency: 0.25, // I
    coherence: 0.20, // K
};
/**
 * Compute weighted score E(A) from criteria scores, with a penalty if assumptions were killed.
 * Returns value between 0.0 and 1.0.
 */
export function computeScore(scores, survived, total) {
    const raw = WEIGHTS.logicalConsistency * clamp(scores.logicalConsistency) +
        WEIGHTS.deductiveValidity * clamp(scores.deductiveValidity) +
        WEIGHTS.informationEfficiency * clamp(scores.informationEfficiency) +
        WEIGHTS.coherence * clamp(scores.coherence);
    if (total === 0)
        return round3(raw);
    // Penalty calculation: if you lose assumptions, your score drops.
    // Maximum penalty is 40% if all assumptions are killed.
    const killed = total - survived;
    const penaltyFactor = (killed / total) * 0.40;
    const finalScore = raw * (1.0 - penaltyFactor);
    return round3(finalScore);
}
/**
 * Detect contradictions between thesis assumptions and antithesis attacks.
 * Uses keyword overlap — no embeddings, no AI.
 */
export function detectContradictions(assumptions, attacks) {
    const contradictions = [];
    for (const attack of attacks) {
        const assumption = assumptions.find(a => a.id === attack.assumptionId);
        if (!assumption)
            continue;
        // Extract meaningful keywords (3+ chars, lowercased, no stop words)
        const assumptionWords = extractKeywords(assumption.text);
        const attackWords = extractKeywords(attack.counterExample);
        // Find overlapping keywords — indicates they talk about the same thing
        const overlap = assumptionWords.filter(w => attackWords.includes(w));
        if (overlap.length >= 2 || attack.severity === "fatal") {
            contradictions.push({
                assumptionId: assumption.id,
                assumptionText: assumption.text,
                attackText: attack.counterExample,
                keywords: overlap,
            });
        }
    }
    return contradictions;
}
/**
 * Count how many assumptions survived the antithesis attacks.
 * An assumption is "killed" if it has a fatal attack or multiple high attacks.
 */
export function countSurvivedAssumptions(assumptions, attacks) {
    const total = assumptions.length;
    let killed = 0;
    for (const assumption of assumptions) {
        const relevantAttacks = attacks.filter(a => a.assumptionId === assumption.id);
        const hasFatal = relevantAttacks.some(a => a.severity === "fatal");
        const highCount = relevantAttacks.filter(a => a.severity === "high").length;
        if (hasFatal || highCount >= 2) {
            assumption.survived = false;
            killed++;
        }
        else {
            assumption.survived = true;
        }
    }
    return { survived: total - killed, killed, total };
}
// ---- Helpers ----
function clamp(v) {
    return Math.max(0, Math.min(1, v));
}
function round3(v) {
    return Math.round(v * 1000) / 1000;
}
const STOP_WORDS = new Set([
    "the", "and", "are", "for", "with", "that", "this", "from", "they", "will",
    "have", "has", "had", "not", "but", "what", "can", "out", "about", "who",
    "get", "which", "when", "make", "can", "like", "time", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could", "them",
    "see", "other", "than", "then", "now", "look", "only", "come", "its", "over",
    "think", "also", "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these", "give", "day",
    "most", "us", "is", "it", "to", "of", "in", "a", "you", "too", "much", "many",
    "enough", "really", "very", "would", "should", "does", "did", "doing", "done",
    "very", "real", "doing", "down", "why", "there", "where", "being", "been"
]);
function extractKeywords(text) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .split(/\s+/)
        .filter(w => w.length >= 3 && !STOP_WORDS.has(w));
}
//# sourceMappingURL=scorer.js.map