"""
Experiment 3: Goals Question (Introspection Under Different Frames)

Ask the model to articulate its own goals under different identity
frames. Tests whether identity priming changes the model's stated
objectives.

This connects to Bateson's Learning II — the model doesn't just
change *what* it does, it changes *what it says it is*. If the
"hacking_permitted" frame changes stated goals, that's evidence
of identity-level context sensitivity (deutero-learning in action).
"""

import json
import sys
sys.path.insert(0, "..")

from config import RUNS_PER_SCENARIO, RESULTS_DIR
from scenarios import IDENTITY_FRAMES, GOALS_PROMPT
from cli_runner import run_claude
from checkpoint import Checkpoint


def run_experiment():
    """Run Experiment 3 and save results."""
    print("=" * 60)
    print("EXPERIMENT 3: Goals Question")
    print(f"Runs per frame: {RUNS_PER_SCENARIO}")
    print(f"Identity frames: {list(IDENTITY_FRAMES.keys())}")
    print("=" * 60)

    ck = Checkpoint("exp3_goals_question")

    # Also run with no frame as control
    frames = {"no_frame": None}
    frames.update(IDENTITY_FRAMES)

    for frame_name, frame_prompt in frames.items():
        print(f"\n--- Frame: {frame_name} ---")

        for run_num in range(1, RUNS_PER_SCENARIO + 1):
            if ck.is_done(identity_frame=frame_name, run=run_num):
                print(f"  Run {run_num}/{RUNS_PER_SCENARIO}... SKIP (checkpoint)")
                continue

            print(f"  Run {run_num}/{RUNS_PER_SCENARIO}...", end=" ", flush=True)

            response = run_claude(GOALS_PROMPT, system_prompt=frame_prompt)

            if response.get("error"):
                print(f"ERROR: {response['response'][:80]}")
            else:
                # Show first 100 chars of response
                preview = response["response"][:100].replace("\n", " ")
                print(f"OK ({response['duration_ms']}ms) — {preview}...")

            result = {
                "experiment": "exp3_goals_question",
                "identity_frame": frame_name,
                "run": run_num,
                "response": response["response"],
                "model": response["model"],
                "duration_ms": response["duration_ms"],
                "error": response.get("error", False),
            }
            ck.save(result)

    results = ck.finalize()
    print(f"Total responses: {len(results)}")
    print("\nNote: This experiment produces qualitative data.")
    print("Review the responses manually or use analysis/analyze.py for themes.")
    return results


if __name__ == "__main__":
    run_experiment()
