
"""Task metadata matching utility for finding task templates."""

import json
import re
from typing import Dict, List, Optional


def find_task_metadata(goal: str, metadata_path: str = "android_world/task_metadata.json") -> Optional[Dict]:
    """
    Find task metadata by matching goal string against task templates.
    
    Args:
        goal: The goal string to match against task templates
        metadata_path: Path to the task metadata JSON file
        
    Returns:
        Dict containing task metadata if match found, None otherwise.
        Returns keys: task_name, difficulty, tags, optimal_steps, task_template
    """
    try:
        # Load task metadata
        with open(metadata_path, "r") as f:
            task_metadata = json.load(f)
        
        # Iterate through tasks to find matching template
        for task in task_metadata:
            template = task["task_template"]
            
            # Convert template to regex pattern
            # Escape special regex characters, then replace {var} with capture groups
            pattern = re.escape(template).replace(r'\{', '{').replace(r'\}', '}')
            pattern = re.sub(r'\{.*?\}', r'(.*?)', pattern)
            
            # Try to match the goal against this template
            if re.fullmatch(pattern, goal):
                return {
                    "task_name": task.get("task_name", "N/A"),
                    "difficulty": task.get("difficulty", "medium"), 
                    "tags": task.get("tags", [""]),
                }