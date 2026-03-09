// ============================================================
// Sequential Thinking Module (ported from @modelcontextprotocol/server-sequential-thinking)
// ============================================================
// Original: 79 LOC thought logger with branching support.
// Integrated into the unified reasoning engine.
export class SequentialThinkingServer {
    thoughtHistory = [];
    branches = {};
    processThought(input) {
        // Auto-adjust totalThoughts if exceeded
        if (input.thoughtNumber > input.totalThoughts) {
            input.totalThoughts = input.thoughtNumber;
        }
        this.thoughtHistory.push(input);
        // Track branches
        if (input.branchFromThought && input.branchId) {
            if (!this.branches[input.branchId]) {
                this.branches[input.branchId] = [];
            }
            this.branches[input.branchId].push(input);
        }
        return {
            thoughtNumber: input.thoughtNumber,
            totalThoughts: input.totalThoughts,
            nextThoughtNeeded: input.nextThoughtNeeded,
            branches: Object.keys(this.branches),
            thoughtHistoryLength: this.thoughtHistory.length,
        };
    }
}
//# sourceMappingURL=sequential.js.map