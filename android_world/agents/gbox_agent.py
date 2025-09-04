import json
import os
import re
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_world.agents.base_agent import (
    AgentInteractionResult,
    EnvironmentInteractingAgent,
)
from android_world.env import interface

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class GboxAgent(EnvironmentInteractingAgent):
    def __init__(self, env: interface.AsyncEnv, name: str = "FarzanAgent"):
        super().__init__(env, name)

        # Setup task metadata patterns
        with open("android_world/task_metadata.json", "r") as f:
            self.task_patterns = [
                (
                    re.compile(
                        re.sub(
                            r"\{.*?\}",
                            r"(.*?)",
                            re.escape(task["task_template"])
                            .replace(r"\{", "{")
                            .replace(r"\}", "}"),
                        )
                    ),
                    {
                        "task_name": task["task_name"],
                        "tags": task["tags"],
                        "optimal_steps": task["optimal_steps"],
                        "difficulty": task["difficulty"],
                    },
                )
                for task in json.load(f)
            ]

    def reset(self, go_home_on_reset: bool = False) -> None:
        """Resets the agent and environment."""
        super().reset(go_home_on_reset)
        self.env.hide_automation_ui()

    def presetup(self, goal: str) -> None:
        """First step of presetup with context etc."""
        print(f"\n####### 0.PRESETUP #######\n")

        # Get the goal's background info from metadata
        print(f"\n----goal_bg-----\n")
        goal_bg = next(
            (
                metadata
                for pattern, metadata in self.task_patterns
                if pattern.fullmatch(goal)
            ),
            None,
        )

        print(f"---goal_bg---")
        print(f"Matched Task: {goal_bg['task_name']}")
        print(f"Tags: {goal_bg['tags']}")
        print(f"Optimal Steps: {goal_bg['optimal_steps']}")
        print(f"Difficulty: {goal_bg['difficulty']}")
        sys.exit(1)

    def step(self, goal: str) -> AgentInteractionResult:
        print(f"\n####### GOAL #######\n{goal}\n")

        # Go through steps
        self.presetup(goal)

        return AgentInteractionResult(done=False, data=result)
