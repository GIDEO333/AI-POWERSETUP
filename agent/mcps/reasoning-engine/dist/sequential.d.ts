export interface ThoughtInput {
    thought: string;
    nextThoughtNeeded: boolean;
    thoughtNumber: number;
    totalThoughts: number;
    isRevision?: boolean;
    revisesThought?: number;
    branchFromThought?: number;
    branchId?: string;
    needsMoreThoughts?: boolean;
}
export interface ThoughtOutput {
    thoughtNumber: number;
    totalThoughts: number;
    nextThoughtNeeded: boolean;
    branches: string[];
    thoughtHistoryLength: number;
}
export declare class SequentialThinkingServer {
    private thoughtHistory;
    private branches;
    processThought(input: ThoughtInput): ThoughtOutput;
}
//# sourceMappingURL=sequential.d.ts.map