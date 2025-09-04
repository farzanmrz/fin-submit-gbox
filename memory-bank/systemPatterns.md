# System Architecture

## Design Pattern
Multi-Provider Orchestrator Pattern with stateless operation model. The system follows: Request → Analyze → Decide → Execute → Validate.

## Component Relationships
GboxAgent
    LLMOrchestrator (provider-agnostic interface)
        - GeminiProvider
        - OpenAIProvider (future)
        - OllamaProvider (future)
    TaskStep (data structure for individual steps)
        - step_text: Natural language description
        - step_index: Order in sequence
        - gbox_actions: List of associated GBOX actions
        - status: 0=pending, 1=complete
        - attempts, error_messages, result
    EnvironmentInterface (GBOX SDK wrapper)
        - State perception (pixels, UI elements, forest)
        - Action execution (tap, type, swipe)
    TaskManager (manages TaskStep objects in self.init_steps)

## Key Design Decisions
- **Provider Agnostic**: Unified interface allows swapping LLM backends without agent changes
- **Structured Step Management**: TaskStep objects provide stateful tracking of individual steps
- **Incremental Implementation**: Build and test each component independently
- **Semantic Instructions**: Rich context provided to LLM for better understanding
- **Action Association**: Each TaskStep can hold multiple GBOX actions with feedback loop support

## External Validation Mechanism
**CRITICAL**: The AndroidWorld benchmark does NOT use the `data` field in `AgentInteractionResult` to determine task success. Instead, validation occurs externally after the agent completes:

1. **Agent Returns**: `AgentInteractionResult(done=False, data=data)` - The `data` content is ignored for validation
2. **External Check**: Benchmark calls `task.is_successful(env)` on the local Android emulator
3. **Validation Logic**: Each task has specific validation criteria (e.g., `ContactsAddContact` checks if contact exists with exact name/number via `contacts_utils.list_contacts()`)
4. **State Persistence**: Actions performed by Gbox boxes persist on the local emulator even after box termination

**Implication**: Agent success depends on actually performing the required actions on the device, not on returning specific data structures.

## Core Data Patterns
```python
# State access pattern
state = self.get_post_transition_state()
ui_elements = state.ui_elements
screen_pixels = state.pixels

# GBOX execution pattern
box = self.gbox.create(type="android", config={...})
result = box.action.ai(instruction="tap login button")
box.terminate(wait=True)

# TaskStep orchestration pattern (STABLE)
resp_thought_orch, resp_steps_orch = self.llm_orchestrator.get_response(goal)
self.init_steps = [
    TaskStep(step_text=step, step_index=idx)
    for idx, step in enumerate(resp_steps_orch)
]

# Action configuration pattern (WORKING)
def _create_gbox_action(self, box, task_step: TaskStep, background_thought: str):
    system_prompt = f"Execute precisely: '{task_step.step_text}'"
    configured_action = partial(
        box.action.ai,
        instruction=task_step.step_text,
        background=background_thought,
        settings={"systemPrompt": system_prompt},
    )
    return configured_action

# DEPRECATED: Complex execution pattern (CAUSES CONFUSION)
# This approach was tried but proved problematic - agent gets confused
for task_step in self.init_steps:
    for act_num, gbox_action in enumerate(task_step.gbox_actions):
        curr_action_result = gbox_action()  # Execute all actions sequentially
        # Problem: Too much happening at once, no validation between steps

# TARGET: Simplified execution pattern (PLANNED)
# Execute one step at a time with validation
first_pending_step = next((step for step in self.init_steps if step.status == 0), None)
if first_pending_step and first_pending_step.gbox_actions:
    action = first_pending_step.gbox_actions[0]
    result = action()
    # Validate result, mark step complete, return to framework
    return AgentInteractionResult(done=False, data={"step": first_pending_step.step_text})
```
