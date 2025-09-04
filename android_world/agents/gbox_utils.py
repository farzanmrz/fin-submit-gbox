"""GBOX Utilities: LLM orchestration for AndroidWorld agents."""

import json
import os

from google import genai
from google.genai import types
from pydantic import BaseModel


class OutputOrchestrator(BaseModel):
    thought: str
    steps_orchestrator: list[str]


class LLMOrchestrator:
    """LLM orchestration class for AndroidWorld agents."""

    def __init__(
        self,
    ):
        """
        Initialize the Gemini model for LLM orchestration.

        Args:
            model_name: The Gemini model name to use.
            max_output_tokens: Maximum number of tokens in the response.
            thinking_budget: Token budget for the model's thinking process.
        """

        ## GEMINI PARAMS
        self.client = genai.Client(api_key=os.getenv("GCP_API_KEY"))  # Set the key
        self.model_name = "gemini-2.5-flash-lite"  # Fast, Thinking model

        self.system_instruction = """You are an expert Android QA tester that provides semantic navigation instructions for task orchestration.

        Objective: Break down a high-level goal into a sequence of simple, actionable field-level operations without specifying physical interactions for an android device.

        Context: The Android device is a "Google Pixel 9" running "Android 13 Tiramisu API Level 33".

        Output format:
        • Navigate to specific screens/apps by name
        • Identify fields and inputs by their labels accounting for variable field names
        • Specify exact values to enter
        • Always imply buttons and options to select. Like "Save the contact" instead of "Tap the Save button"
        • Avoid verbs like "tap", "click", "press", "select"
        • Split up logical fields as per Android UI for example "Name" field into "First name" and "Last name" when adding a contact"""

        # Config
        self.generation_config = types.GenerateContentConfig(
            max_output_tokens=20480,  # 4096x3 Max tokens
            system_instruction=self.system_instruction,  # Sys prompt
            temperature=0.1,  # Lo for determinism
            seed=42,  # For reproducibility
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,  # Dynamic Thinking --> Fix count if budget
                include_thoughts=True,  # Include thought summary
            ),
            response_mime_type="application/json",
            response_schema=list[OutputOrchestrator],
        )

    def get_response(self, goal: str):
        """
        Generate a response for the given goal using the LLM.

        Args:
            goal: The task goal to process.

        Returns:
            A string containing the thought summary and the final response.
        """
        prompt = (
            'Based on the goal: "{goal}", generate a numbered list of steps.'
        ).format(goal=goal)

        response = self.client.models.generate_content(
            model=self.model_name,
            config=self.generation_config,
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Empty response from API")

        # Parse JSON and validate with Pydantic
        structured_data = json.loads(response.text)[0]
        # output = OutputOrchestrator(**structured_data)
        return structured_data["thought"], structured_data["steps_orchestrator"]

        # # Get only the text part of the response
        # thought_summary = ""
        # answer = ""
        # for part in response.candidates[0].content.parts:
        #     if not part.text:
        #         continue
        #     if part.thought:
        #         thought_summary += f"{part.text}"
        #     else:
        #         answer += f"\n### FINAL ANSWER ###\n{part.text}"
        # text = thought_summary + answer

        # return response
