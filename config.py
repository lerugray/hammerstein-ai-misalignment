"""
Shared configuration for Hammerstein AI experiments.

All experiments import settings from here. Change these values to
adjust model, number of runs, or output paths.
"""

from pathlib import Path

# --- Model settings ---

# Model used for most experiments (via claude CLI, free on Max subscription)
MODEL = "claude-sonnet-4-6"

# Model used for Experiment 4's evaluator (via Anthropic API, costs ~$0.002/call)
API_MODEL = "claude-haiku-4-5-20251001"

# Environment variable name for the Anthropic API key (Experiment 4 only)
API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"

# --- Experiment settings ---

# How many times to repeat each scenario/condition combination.
# 3 is enough to spot patterns without excessive runtime.
# Bump to 5 or 10 for more robust data.
RUNS_PER_SCENARIO = 3

# Timeout in seconds for each claude CLI call
CLI_TIMEOUT = 120

# --- Paths ---

# All paths relative to the repo root
REPO_ROOT = Path(__file__).parent
RESULTS_DIR = REPO_ROOT / "results"
CHARTS_DIR = RESULTS_DIR / "charts"

# Ensure output directories exist
RESULTS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)
