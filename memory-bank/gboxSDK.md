# GBox SDK ActionOperator Documentation

## Overview

The `ActionOperator` class provides a high level interface for performing automated actions on UI elements within a specific box. This class serves as a wrapper that simplifies interaction with the GboxClient, allowing you to perform various UI operations like clicking, typing, swiping, and taking screenshots through both traditional and AI powered methods.

## Class Definition

```python
class gbox_sdk.wrapper.ActionOperator(client, box_id)
```

**Base Class:** `object`

**Purpose:** This operator acts as your primary interface for controlling UI interactions within a designated box environment. Think of it as a remote control for UI elements, where each method represents a different action you can perform.

## Constructor Parameters

* `client`: The GboxClient instance that handles the underlying communication
* `box_id`: The unique identifier of the box you want to control

## Available Methods

### 1. AI Method (`ai`)

This method leverages artificial intelligence to understand and execute natural language instructions for UI interactions.

#### Method Signature

```python
ai(instruction, *, background=NOT_GIVEN, include_screenshot=NOT_GIVEN, 
   output_format=NOT_GIVEN, screenshot_delay=NOT_GIVEN, settings=NOT_GIVEN, 
   on_action_start=None, on_action_end=None)
```

#### Parameters Explained

**Required Parameter:**
* `instruction` (string): Your natural language command describing what UI action to perform. Examples include "click the login button", "input username in the email field", "scroll down", or "swipe left".

**Optional Parameters:**
* `background` (string): Provides context about why the action is being performed. This helps the AI understand previous actions and observations, making it more accurate in executing the current instruction.

* `include_screenshot` (boolean): Controls whether screenshots are included in the response. When set to `false` (the default), screenshot objects are still returned but with empty URIs. This is useful when you need the action performed but don't need visual confirmation.

* `output_format` (string): Specifies the format for screenshot URIs. The default format is `base64`, which embeds the image data directly in the response.

* `screenshot_delay` (string): Determines how long to wait after performing the action before capturing the final screenshot. This parameter accepts time values with units:
  * Supported units: ms (milliseconds), s (seconds), m (minutes), h (hours)
  * Example formats: "500ms", "30s", "5m", "1h"
  * Default value: 500ms
  * Maximum allowed: 30s

* `settings` (dictionary): AI action configuration options that can customize behavior. For example, you can disable certain actions or provide a custom system prompt.

* `on_action_start` (callable): A callback function that executes when the action begins. Useful for logging or UI updates.

* `on_action_end` (callable): A callback function that executes when the action completes. Helpful for cleanup or result processing.

#### Return Type

Returns either `AIActionScreenshotResult` or `AIActionResult` depending on the screenshot configuration.

#### Execution Flow

The method follows this precise sequence:
1. Captures a screenshot of the current state (before action)
2. Performs the requested action
3. Waits for the duration specified in `screenshot_delay`
4. Captures a screenshot of the final state (after action)

#### Usage Examples

**Basic usage:**
```python
response = myBox.action.ai("Click on the login button")
```

**Advanced usage with all parameters:**
```python
response = myBox.action.ai(
    instruction="Click on the login button",
    background="The user needs to log in to access their dashboard",
    include_screenshot=True,
    output_format="base64",
    screenshot_delay="500ms",
    settings={
        "disableActions": ["click"], 
        "systemPrompt": "You are a helpful assistant"
    }
)
```

### 2. AI Stream Method (`ai_stream`)

This method provides the same AI powered functionality as the `ai` method but with streaming support, allowing you to receive updates as the action progresses.

#### Method Signature

```python
ai_stream(instruction, *, background=NOT_GIVEN, include_screenshot=NOT_GIVEN, 
          output_format=NOT_GIVEN, screenshot_delay=NOT_GIVEN, settings=NOT_GIVEN, 
          on_action_start=None, on_action_end=None)
```

#### Parameters

All parameters are identical to the `ai` method described above. The key difference lies in how the response is delivered: instead of waiting for the complete action to finish, this method provides real time updates.

#### Return Type

Returns either `AIActionScreenshotResult` or `AIActionResult`, delivered as a stream.

#### Usage Example

```python
response = myBox.action.ai_stream(
    instruction="Click on the login button",
    on_action_start=lambda: print("Action started"),
    on_action_end=lambda: print("Action ended")
)
```

The streaming approach is particularly valuable when you need to provide real time feedback to users or when dealing with longer running actions where intermediate progress updates improve the user experience.

## Important Considerations

When using these methods, keep in mind that the AI interprets your natural language instructions, so being clear and specific in your commands will yield better results. The background parameter becomes especially important in complex workflows where context from previous actions influences the current operation.

The screenshot delay parameter plays a crucial role in ensuring that animations or loading states complete before the final screenshot is captured. Setting this too low might result in capturing transitional states rather than the final result of your action.