// ============================================================
// Thesis-Antithesis Engine — State Machine
// ============================================================
// Manages thesis-antithesis sessions with phase gates, state tracking,
// and integration with scorer for contradiction detection.

import type {
  Phase, ThesisAntithesisInput, ThesisAntithesisOutput, SessionState,
  Assumption, Attack, Contradiction
} from './types.js';
import { PHASE_ORDER } from './types.js';
import { computeScore, detectContradictions, countSurvivedAssumptions } from './scorer.js';

export class ThesisAntithesisEngine {
  private sessions: Map<string, SessionState> = new Map();

  /**
   * Process a thesis-antithesis tool call.
   * Enforces phase ordering, stores state, computes scores.
   */
  processPhase(input: ThesisAntithesisInput): ThesisAntithesisOutput {
    // Get or create session
    const session = this.getOrCreateSession();
    const { phase } = input;

    // ---- PHASE GATE: enforce ordering ----
    const gateError = this.checkPhaseGate(session, phase);
    if (gateError) {
      return this.errorOutput(session, gateError);
    }

    // ---- Process each phase ----
    let contradictions: Contradiction[] = [];

    switch (phase) {
      case "thesis":
        // Enforce minimum assumptions
        if (!input.assumptions || input.assumptions.length === 0) {
          return this.errorOutput(session, "Thesis must include at least 1 explicit assumption. List your assumptions with unique IDs.");
        }
        session.thesis = {
          content: input.content,
          assumptions: input.assumptions,
        };
        break;

      case "antithesis": {
        const attacks = input.attacks ?? [];
        
        // Enforce minimum attack count
        if (attacks.length === 0) {
          return this.errorOutput(session, "Antithesis must include at least 1 attack. Challenge your thesis assumptions.");
        }
        
        // Enforce minimum adversarial pressure
        if (!attacks.some(a => a.severity === "high" || a.severity === "fatal")) {
          return this.errorOutput(session, "Antithesis must contain at least one attack with 'high' or 'fatal' severity. Don't be too easy on your thesis.");
        }

        session.antithesis = {
          content: input.content,
          attacks: attacks,
        };

        // Run contradiction detection
        if (session.thesis) {
          contradictions = detectContradictions(
            session.thesis.assumptions,
            session.antithesis.attacks
          );
          session.contradictions = contradictions;

          // Count survived assumptions
          countSurvivedAssumptions(
            session.thesis.assumptions,
            session.antithesis.attacks
          );
        }
        break;
      }

      case "synthesis": {
        const scores = input.scores ?? null;
        
        // Pass survival stats to penalize self-assigned score if thesis was destroyed
        const totalAsms = session.thesis?.assumptions.length ?? 0;
        const survivedAsms = session.thesis?.assumptions.filter(a => a.survived === true).length ?? 0;
        
        const sessionScore = scores ? computeScore(scores, survivedAsms, totalAsms) : null;
        
        session.synthesis = {
          content: input.content,
          scores,
          sessionScore,
        };
        break;
      }

      case "stresstest": {
        // Cap confidence based on assumption survival rate
        let confidence = input.confidence ?? 0;
        const totalAsms2 = session.thesis?.assumptions.length ?? 0;
        const survivedAsms2 = session.thesis?.assumptions.filter(a => a.survived === true).length ?? 0;
        
        if (totalAsms2 > 0) {
          // Max confidence = 0.50 + 0.50 * (survived/total)
          // If 0/3 survive, max = 0.50. If 1/3, max = 0.67. If 3/3, max = 1.0.
          const maxConfidence = 0.50 + 0.50 * (survivedAsms2 / totalAsms2);
          if (confidence > maxConfidence) {
            confidence = Math.round(maxConfidence * 100) / 100;
          }
        }
        
        session.stresstest = {
          content: input.content,
          results: input.stressResults ?? [],
          premortem: input.premortem ?? '',
          confidence,
        };
        break;
      }
    }

    // Mark phase complete
    session.currentPhase = phase;
    if (!session.phasesCompleted.includes(phase)) {
      session.phasesCompleted.push(phase);
    }

    // Determine next phase
    const phaseIdx = PHASE_ORDER.indexOf(phase);
    const nextPhase = phaseIdx < PHASE_ORDER.length - 1
      ? PHASE_ORDER[phaseIdx + 1]
      : null;

    // Build output
    const assumptionCount = session.thesis?.assumptions.length ?? 0;
    const survived = session.thesis?.assumptions.filter(a => a.survived === true).length ?? null;

    return {
      phase,
      phaseComplete: true,
      nextPhaseRequired: nextPhase,
      sessionId: session.id,
      phasesCompleted: [...session.phasesCompleted],
      assumptionCount,
      assumptionsSurvived: session.phasesCompleted.includes("antithesis") ? survived : null,
      contradictionsFound: session.contradictions,
      sessionScore: session.synthesis?.sessionScore ?? null,
      confidence: session.stresstest?.confidence ?? null,
      summary: this.buildSummary(session, phase),
    };
  }

  /**
   * Reset all sessions (useful for testing).
   */
  reset(): void {
    this.sessions.clear();
  }

  // ---- Private ----

  private getOrCreateSession(): SessionState {
    // For simplicity, one active session. Could be extended with sessionId param.
    const activeId = "active";
    let session = this.sessions.get(activeId);

    if (!session) {
      session = {
        id: this.generateId(),
        createdAt: Date.now(),
        currentPhase: null,
        phasesCompleted: [],
        thesis: null,
        antithesis: null,
        synthesis: null,
        stresstest: null,
        contradictions: [],
      };
      this.sessions.set(activeId, session);
    }

    // If all phases completed, start a new session
    if (session.phasesCompleted.length === 4) {
      const newSession: SessionState = {
        id: this.generateId(),
        createdAt: Date.now(),
        currentPhase: null,
        phasesCompleted: [],
        thesis: null,
        antithesis: null,
        synthesis: null,
        stresstest: null,
        contradictions: [],
      };
      this.sessions.set(activeId, newSession);
      return newSession;
    }

    return session;
  }

  private checkPhaseGate(session: SessionState, requestedPhase: Phase): string | null {
    const reqIdx = PHASE_ORDER.indexOf(requestedPhase);

    // Thesis can always be called (starts or restarts session)
    if (requestedPhase === "thesis") return null;

    // Check all prerequisite phases are completed
    for (let i = 0; i < reqIdx; i++) {
      const prereq = PHASE_ORDER[i];
      if (!session.phasesCompleted.includes(prereq)) {
        return `Phase gate violation: "${requestedPhase}" requires "${prereq}" to be completed first. ` +
               `Completed phases: [${session.phasesCompleted.join(', ')}]. ` +
               `Call phase="${prereq}" first.`;
      }
    }

    return null;
  }

  private buildSummary(session: SessionState, currentPhase: Phase): string {
    switch (currentPhase) {
      case "thesis": {
        const count = session.thesis?.assumptions.length ?? 0;
        return `Thesis recorded with ${count} explicit assumption(s). Proceed to antithesis to challenge them.`;
      }
      case "antithesis": {
        const attacks = session.antithesis?.attacks.length ?? 0;
        const contradictions = session.contradictions.length;
        const survived = session.thesis?.assumptions.filter(a => a.survived === true).length ?? 0;
        const total = session.thesis?.assumptions.length ?? 0;
        return `Antithesis recorded with ${attacks} attack(s). ` +
               `${contradictions} contradiction(s) detected. ` +
               `${survived}/${total} assumption(s) survived. ` +
               `Proceed to synthesis to score and merge.`;
      }
      case "synthesis": {
        const score = session.synthesis?.sessionScore;
        return score !== null
          ? `Synthesis complete. Session score E(A) = ${score}. Proceed to stresstest for final validation.`
          : `Synthesis recorded without scores. Proceed to stresstest.`;
      }
      case "stresstest": {
        const conf = session.stresstest?.confidence ?? 0;
        const results = session.stresstest?.results ?? [];
        const passed = results.filter(r => r.outcome === "pass").length;
        const failed = results.filter(r => r.outcome === "fail").length;
        const score = session.synthesis?.sessionScore ?? 'N/A';
        return `Thesis-antithesis reasoning complete. ` +
               `Final confidence: ${(conf * 100).toFixed(0)}%. ` +
               `Stress tests: ${passed} passed, ${failed} failed. ` +
               `Session score: ${score}. ` +
               `Session finished — next call starts a fresh session.`;
      }
      default:
        return '';
    }
  }

  private errorOutput(session: SessionState, error: string): ThesisAntithesisOutput {
    return {
      phase: session.currentPhase ?? "thesis",
      phaseComplete: false,
      nextPhaseRequired: null,
      sessionId: session.id,
      phasesCompleted: [...session.phasesCompleted],
      assumptionCount: session.thesis?.assumptions.length ?? 0,
      assumptionsSurvived: null,
      contradictionsFound: [],
      sessionScore: null,
      confidence: null,
      summary: `ERROR: ${error}`,
    };
  }

  private generateId(): string {
    return `de-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
  }
}
