"""FarzanAgent: A minimal custom agent template for AndroidWorld with GBOX integration."""

import os
import re
import sys
from functools import partial

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import webbrowser

from dotenv import load_dotenv
from gbox_sdk import GboxSDK

from android_world import checkpointer as checkpointer_lib
from android_world import registry, suite_utils
from android_world.agents.base_agent import (
    AgentInteractionResult,
    EnvironmentInteractingAgent,
)
from android_world.env import env_launcher, interface

from .gbox_utils import LLMOrchestrator

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

"""
Part 1. Task Step
"""


class TaskStep:
    """Class representing a single step in a task."""

    def __init__(self, step_text: str, step_index: int):
        self.step_text = step_text  # Natural language description
        self.step_index = step_index  # Order in sequence
        self.gbox_actions = []  # List of associated GBOX actions
        self.status = 0  # 1=done, 0=pending
        self.attempts = 0  # Number of attempts
        self.error_messages = []  # List of error messages
        self.result = None  # Result of the step execution


"""
Part 2. Agent Setup - Testing
"""


class GboxAgent(EnvironmentInteractingAgent):
    """GBOX Agent Setup for Challenge 2"""

    def __init__(self, env: interface.AsyncEnv, name: str = "FarzanAgent"):
        super().__init__(env, name)

        # Setup SDKs
        self.gbox = GboxSDK(api_key=os.getenv("GBOX_API_KEY"))
        self.device_id = os.getenv("GBOX_DEVICE_ID")

        # Initialize LLM orchestrator
        self.llm_orchestrator = LLMOrchestrator()

        # Initialize task steps list
        self.init_steps = []

        # Configuration

    def reset(self, go_home_on_reset: bool = False) -> None:
        """Resets the agent and environment."""
        super().reset(go_home_on_reset)
        self.env.hide_automation_ui()

    def _create_gbox_action(self, box, task_step: TaskStep, background_thought: str):
        """Creates a pre-configured, callable GBOX action for a given TaskStep."""
        system_prompt = (
            "You are a focused Android assistant. Your immediate goal is to execute "
            f"the following instruction precisely: '{task_step.step_text}'"
        )

        # Use functools.partial to create a clean, callable action
        # without executing it immediately.
        configured_action = partial(
            box.action.ai,
            instruction=task_step.step_text,
            background=background_thought,
            settings={"systemPrompt": system_prompt},
        )
        return configured_action

    def step(self, goal: str) -> AgentInteractionResult:
        """Perform a single step using GBOX and a simple LLM planner."""

        ## INIT VARS
        state = self.get_post_transition_state()

        ## DEBUG PRINT
        print(f"\n\n####### YOUR STUFF #######")

        print(f"\n\n####### STATE OBJECT #######")
        # print(f"\nstate.pixels:")
        # print(state.pixels)

        # print(f"\nstate.forest:")
        # print(state.forest)

        print(f"\n\n####### ENVIRONMENT OBJECT #######")
        print(f"\nself.env.foreground_activity_name:")
        print(self.env.foreground_activity_name)

        print(f"\n####### GOAL #######\n\n{goal}\n\n")

        ## ORCHESTRATION
        # Generate response using LLM orchestrator
        resp_thought_orch, resp_steps_orch = self.llm_orchestrator.get_response(goal)

        ## DEBUG PRINT
        print(f"\n####### ORCHESTRATOR THOUGHT #######\n{resp_thought_orch}\n\n")

        # Initialize the received steps as TaskStep objects
        self.init_steps = [
            TaskStep(step_text=step, step_index=idx)
            for idx, step in enumerate(resp_steps_orch)
        ]

        # Create the GBOX box instance
        box = self.gbox.create(
            type="android",
            config={
                "labels": {"gbox.ai/device-id": self.device_id},
                "cpu": 8,
                "memory": 16384,
                "storage": 128,
            },
        )

        # Open the live view in a web browser for monitoring
        live_view = box.live_view()
        webbrowser.open(live_view.url)

        # Populate gbox_actions using the new helper method
        for task_step in self.init_steps:
            action_callable = self._create_gbox_action(
                box, task_step, resp_thought_orch
            )
            task_step.gbox_actions.append(action_callable)

        ## DEBUG PRINT Task Steps
        print("\n####### TASK STEPS #######")
        for task_step in self.init_steps:
            print(f"{task_step.step_index}: '{task_step.step_text}'")

        ## DEBUG PRINT Execution Workflow
        print("\n####### EXECUTION WORKFLOW #######")

        # Loop through all steps
        for task_step in self.init_steps:

            ## DEBUG PRINT Current Step
            print(
                f"\n--- CURR STEP {task_step.step_index} ({len(task_step.gbox_actions)} Actions): '{task_step.step_text}'---\n"
            )

            # List to hold results of all actions in this step
            action_results = []

            # Loop through all actions in the current step
            for act_num, gbox_action in enumerate(task_step.gbox_actions):
                print(f"\n\t - ACTION {act_num}\n")

                try:
                    # Execute the action
                    curr_action_result = gbox_action()

                    ## DEBUG PRINT Action Result
                    print(f"\nOUTPUT:\n{curr_action_result.output}")
                    print(
                        f"\n\nAIRESP MESSAGES:\n{curr_action_result.ai_response.messages}"
                    )
                    print(
                        f"\nAIRESP ACTIONS:\n{curr_action_result.ai_response.actions}"
                    )
                    print(
                        f"\nAIRESP REASONING:\n{curr_action_result.ai_response.reasoning}"
                    )
                    print(f"\nAIRESP MODEL:\n{curr_action_result.ai_response.model}")

                    # Update action results
                    action_results.append(curr_action_result)

                except Exception as e:
                    # Handle exceptions and log error messages
                    error_msg = str(e)
                    print(f"Action Error: {error_msg}")
                    task_step.attempts += 1
                    task_step.error_messages.append(error_msg)

            # Update TaskStep status after all actions
            task_step.status = 1  # Mark as done
            task_step.result = action_results

        # Terminate the box after action
        # box.terminate(wait=True)

        # sys.exit(1)  # We still exit after the first action for now

        # tasks = [re.sub(r"^\d+\.\s*", "", line).strip() for line in text.split("\n")]
        # for task in tasks:
        #     if not task:
        #         continue
        #     print(f"Executing task: '{task}'")
        #     box.action.ai(task)

        #     box.terminate(wait=True)

        # data = {
        #     "goal": goal,
        #     "note": "GBOX Agent executed successfully.",
        # }
        # return AgentInteractionResult(done=False, data=data)
