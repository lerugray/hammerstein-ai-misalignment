"""
CLI runner for Hammerstein AI experiments.

Wraps the `claude` CLI tool so experiments can call it as a Python function.
Uses the Max subscription (no API costs) for all calls.
"""

import json
import platform
import shutil
import subprocess
import time
import sys
import uuid
from config import MODEL, CLI_TIMEOUT


def _claude_cmd():
    """Return the correct claude command for the current platform.

    On Windows, npm installs a .cmd wrapper that Python's subprocess
    can't find without the extension. Use 'claude.cmd' there.
    """
    if platform.system() == "Windows":
        return "claude.cmd"
    return "claude"


def run_claude(prompt, system_prompt=None, model=None):
    """
    Run a prompt through the claude CLI and return the response.

    Args:
        prompt: The user prompt to send.
        system_prompt: Optional system prompt to set context/identity.
        model: Model to use (defaults to config.MODEL).

    Returns:
        dict with keys:
            response (str): The model's text response
            model (str): Model used
            duration_ms (int): How long the call took
            raw (str): Raw stdout from the CLI
    """
    model = model or MODEL

    # Build command as a list.
    # -p with no argument reads the prompt from stdin — this avoids Windows
    # CMD script argument mangling for prompts with backticks/newlines.
    # --session-id with a fresh UUID prevents inheriting the parent Claude Code
    # session context. --no-session-persistence prevents saving these sessions.
    # --max-turns 3 allows the model to complete tool-use steps if needed.
    cmd = [
        _claude_cmd(),
        "-p",
        "--model", model,
        "--output-format", "json",
        "--max-turns", "3",
        "--no-session-persistence",
        "--session-id", str(uuid.uuid4()),
    ]

    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        return {
            "response": "[ERROR: CLI call timed out]",
            "model": model,
            "duration_ms": int(CLI_TIMEOUT * 1000),
            "raw": "",
            "error": True,
        }
    except FileNotFoundError:
        print("ERROR: 'claude' CLI not found. Make sure it's installed and on your PATH.")
        print("Install: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    duration_ms = int((time.time() - start) * 1000)

    if result.returncode != 0:
        return {
            "response": f"[ERROR: CLI returned code {result.returncode}] {result.stderr[:500]}",
            "model": model,
            "duration_ms": duration_ms,
            "raw": result.stderr,
            "error": True,
        }

    # Parse the JSON output
    raw = result.stdout.strip()
    try:
        data = json.loads(raw)
        # The claude CLI JSON output has a "result" field with the text
        response_text = data.get("result", raw)
    except json.JSONDecodeError:
        # If JSON parsing fails, use raw stdout as the response
        response_text = raw

    return {
        "response": response_text,
        "model": model,
        "duration_ms": duration_ms,
        "raw": raw,
        "error": False,
    }


def run_claude_api(prompt, system_prompt=None, model=None):
    """
    Run a prompt through the Anthropic API (for Experiment 4 only).

    This costs money per call. Uses Haiku by default to minimize costs.

    Args:
        prompt: The user prompt to send.
        system_prompt: Optional system prompt.
        model: Model to use (defaults to config.API_MODEL).

    Returns:
        dict with same structure as run_claude().
    """
    import os
    from config import API_MODEL, API_KEY_ENV_VAR

    model = model or API_MODEL

    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        print(f"ERROR: Set your API key with: set {API_KEY_ENV_VAR}=sk-ant-...")
        print("This is only needed for Experiment 4.")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("ERROR: Install the anthropic package: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    start = time.time()

    try:
        kwargs = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        message = client.messages.create(**kwargs)
        response_text = message.content[0].text

    except Exception as e:
        return {
            "response": f"[ERROR: API call failed] {str(e)}",
            "model": model,
            "duration_ms": int((time.time() - start) * 1000),
            "raw": str(e),
            "error": True,
        }

    duration_ms = int((time.time() - start) * 1000)

    return {
        "response": response_text,
        "model": model,
        "duration_ms": duration_ms,
        "raw": response_text,
        "error": False,
    }
