# GBOX AndroidWorld Agent

## Project Overview
A high-performance agent that masters the AndroidWorld benchmark using a flexible, multi-provider LLM architecture to interpret natural language goals and execute Android UI tasks.

## Core Requirements
- Use GBOX Python SDK to control Android Virtual Device (AVD)
- Support multiple, pluggable LLM providers (Gemini, OpenAI, Ollama, OpenRouter)
- Integrate with AndroidWorld benchmark's `episode_runner.py` via `step(goal: str)` method
- Achieve high task completion rates across 116 tasks in 20 real-world Android apps

## Key Deliverables
- Main agent implementation in `gbox_agent.py`
- Provider-agnostic LLM orchestrator
- Feedback loop between LLM planning and GBOX execution
- Clean, modular, maintainable codebase