# Technical Environment

## Technology Stack
* Language: Python 3.9+
* Framework: Google AndroidWorld Benchmark
* SDK: GBOX Python SDK
* LLM: Google Gemini API (primary), OpenAI/Ollama (planned)
* Testing: AndroidWorld task suite (116 tasks)

## Development Setup

### Prerequisites
1. Android Studio with SDK tools
2. GBOX CLI installed and configured
3. Python environment with dependencies
4. API keys for LLM providers

### M1 Mac Specific Configuration

Add these lines to your ~/.zshrc file:

export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
pgrep -f gbox-device-proxy > /dev/null || nohup ~/.gbox/device-proxy/gbox-device-proxy --on-demand > /dev/null 2>&1 &

For the AVD system image, use the ARM compatible version. Install via SDK Manager: "Google APIs ARM 64 v8a System Image" (API Level 33)

### Execution Workflow

Terminal 1: Start AVD
~/Library/Android/sdk/emulator/emulator -avd AndroidWorldAvd -no-snapshot -grpc 8554

Terminal 2: Connect GBOX
gbox device-connect emulator-5554-usb --background

Terminal 3: Run agent
python run.py --suite_family=android_world --tasks=ContactsAddContact --agent_name=gbox_agent -adb_path=$HOME/Library/Android/sdk/platform-tools/adb --task_random_seed=42 --fixed_task_seed=True

## Configuration Options

suite_family: Benchmark suite selection (android_world, miniwob)
tasks: Comma separated list of task names to execute
agent_name: Specifies which agent implementation to use
n_task_combinations: Number of variations per task (default: 1)
task_random_seed: Seed for reproducible testing
fixed_task_seed: Boolean to maintain consistent seed across combinations
adb_path: Full path to Android Debug Bridge executable

## Project Structure
* Active Development: android_world/agents/gbox_agent.py
* Baseline Reference: android_world/agents/farzan_agent.py
* Entry Point: run.py
* Orchestrator: LLMOrchestrator class with provider abstraction
* Environment Interface: GBOX SDK wrapper for Android control

## Dependencies
* gbox-python-sdk: Device automation
* google-generativeai: Gemini API client
* androidworld: Benchmark framework
* Standard Python libraries: sys, json, logging, typing