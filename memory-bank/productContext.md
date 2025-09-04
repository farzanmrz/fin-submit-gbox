# Product Context

## Problem Statement
Android automation requires robust understanding of natural language instructions, accurate perception of UI state, and reliable execution of complex action sequences. Current solutions lack flexibility in LLM provider selection and struggle with multi-step task planning.

## Solution Approach
The agent solves these challenges through:
- **Dynamic LLM Selection**: Choose appropriate models based on task complexity
- **Semantic Understanding**: Rich system instructions for contextual awareness
- **Feedback Loop Architecture**: Orchestrator output drives GBOX execution with validation
- **Stateless Processing**: Each step analyzed with fresh context to avoid state drift

## User Workflow
1. User starts AVD and registers with GBOX CLI
2. Benchmark presents natural language goal
3. Agent orchestrates LLM to break down goal into steps
4. Each step executed via GBOX SDK with validation
5. Results reported back to benchmark framework