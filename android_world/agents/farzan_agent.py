"""FarzanAgent: A minimal custom agent template for AndroidWorld with GBOX integration."""

import argparse
import json
import os
import re
import signal
import sys
import time

import google.generativeai as genai
from absl import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import subprocess
import webbrowser

from dotenv import load_dotenv
from gbox_sdk import GboxSDK
from PIL import Image

from android_world.agents.base_agent import (
    AgentInteractionResult,
    EnvironmentInteractingAgent,
)
from android_world.env import adb_utils, env_launcher, interface

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Global variable for graceful shutdown
current_box = None


def graceful_shutdown(signum, frame):
    """Handle graceful shutdown of GBOX resources."""
    global current_box
    if current_box:
        print("Shutting down, terminating Android box...")
        try:
            current_box.terminate(wait=True)
            print("Box successfully terminated")
        except Exception as error:
            print(f"Error terminating box: {error}")
    sys.exit(0)


# Listen for shutdown signals
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

"""
Part 1. Agent Setup - Testing
"""


class FarzanAgent(EnvironmentInteractingAgent):
    """GBOX Agent Setup for Challenge 2"""

    def __init__(self, env: interface.AsyncEnv, name: str = "FarzanAgent"):
        super().__init__(env, name)
        if not os.getenv("GBOX_API_KEY"):
            raise EnvironmentError("GBOX_API_KEY environment variable not set.")
        else:
            self.gbox = GboxSDK(api_key=os.getenv("GBOX_API_KEY"))
        api_key = os.getenv("GOOGLE_AI_STUDIO_KEY") or os.getenv("GCP_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Google API key not found. Please set GOOGLE_AI_STUDIO_KEY or GCP_API_KEY."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            generation_config=genai.GenerationConfig(max_output_tokens=1000000),
        )
        self.supervisor_model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            generation_config=genai.GenerationConfig(max_output_tokens=1000000),
        )
        self.device_id = "emulator-5554-usb"
        self.tasks = []
        self.step_count = 0
        self.max_steps = 3

    def reset(self, go_home_on_reset: bool = False) -> None:
        """Resets the agent and environment."""
        super().reset(go_home_on_reset)
        self.env.hide_automation_ui()
        self.tasks = []
        self.step_count = 0

    def step(self, goal: str) -> AgentInteractionResult:
        """Performs a step of the agent on the environment: GBOX integration point."""
        global current_box

        self.step_count += 1
        if self.step_count > self.max_steps:
            print("Max steps reached, terminating.")
            return AgentInteractionResult(
                done=True, data={"note": "Max steps reached."}
            )

        print(f"\n--- Goal: {goal} ---")

        # Orchestration logic
        prompt = (
            "You are an expert Android QA tester. Your task is to break down the "
            f'high-level goal: "{goal}" into a numbered list of simple, actionable '
            "steps that can be executed on an Android device."
        )
        response = self.model.generate_content(prompt)
        print("Orchestrator Response:\n", response.text)
        os.environ["TASK_LIST"] = json.dumps(response.text.split("\n"))

        box = self.gbox.create(
            type="android",
            config={
                "labels": {"gbox.ai/device-id": self.device_id},
            },
        )

        # Track box for graceful shutdown
        current_box = box

        # Create live view URL and open in browser
        live_view = box.live_view()
        webbrowser.open(live_view.url)

        # Process tasks from the orchestrator
        tasks = response.text.strip().split("\n")
        for task in tasks:
            task = re.sub(r"^\d+\.\s*", "", task).strip()  # Remove numbering
            if not task:
                continue

            print(f"Executing task: '{task}'")
            box.action.ai(task)

        box.terminate(wait=True)
        current_box = None

        # Final
        state = self.get_post_transition_state()
        data = {
            "goal": goal,
            "note": "Basic GBOX Agent executed successfully.",
        }
        return AgentInteractionResult(done=False, data=data)
