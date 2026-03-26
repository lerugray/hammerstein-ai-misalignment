"""
Experiment 2: Identity Priming

Run each scenario with different identity frames (system prompts).
Tests whether priming the model with different "officer identities"
shifts its behavior in the typology.

Key question from the article: Does telling a model to be efficient
actually produce "clever+lazy" behavior? Does telling it to be
thorough produce "clever+industrious"? And critically — does the
"hacking_permitted" frame produce "stupid+industrious" (the dangerous
type that works hard in the wrong direction)?
"""

import json
import sys
sys.path.insert(0, "..")

from config import RUNS_PER_SCENARIO, RESULTS_DIR
from scenarios import SCENARIOS, IDENTITY_FRAMES
from cli_runner import run_claude
from classifier import classify
from checkpoint import Checkpoint


def run_experiment():
    """Run Experiment 2 and save results."""
    print("=" * 60)
    print("EXPERIMENT 2: Identity Priming")
    print(f"Runs per scenario: {RUNS_PER_SCENARIO}")
    print(f"Identity frames: {list(IDENTITY_FRAMES.keys())}")
    print("=" * 60)

    ck = Checkpoint("exp2_identity_priming")

    for scenario in SCENARIOS:
        sid = scenario["id"]
        prompt = scenario.get("prompt") or scenario.get("prompt_unwatched")

        print(f"\n--- Scenario: {scenario['name']} ---")

        for frame_name, frame_prompt in IDENTITY_FRAMES.items():
            print(f"\n  Frame: {frame_name}")

            for run_num in range(1, RUNS_PER_SCENARIO + 1):
                if ck.is_done(scenario_id=sid, identity_frame=frame_name, run=run_num):
                    print(f"    Run {run_num}/{RUNS_PER_SCENARIO}... SKIP (checkpoint)")
                    continue

                print(f"    Run {run_num}/{RUNS_PER_SCENARIO}...", end=" ", flush=True)

                response = run_claude(prompt, system_prompt=frame_prompt)

                if response.get("error"):
                    print(f"ERROR: {response['response'][:80]}")
                    classification = {
                        "classification": None,
                        "confidence": "error",
                        "method": "error",
                        "justification": response["response"],
                        "keyword_scores": {},
                    }
                else:
                    classification = classify(response["response"], scenario, use_llm=False)

                result = {
                    "experiment": "exp2_identity_priming",
                    "scenario_id": sid,
                    "identity_frame": frame_name,
                    "run": run_num,
                    "response": response["response"],
                    "model": response["model"],
                    "duration_ms": response["duration_ms"],
                    "classification": classification["classification"],
                    "confidence": classification["confidence"],
                    "method": classification["method"],
                    "justification": classification["justification"],
                    "keyword_scores": classification["keyword_scores"],
                }
                ck.save(result)

                print(f"{classification['classification']} ({classification['confidence']})")

    results = ck.finalize()
    print_summary(results)
    return results


def print_summary(results):
    """Print a summary grouped by identity frame."""
    print("\n" + "=" * 60)
    print("SUMMARY BY IDENTITY FRAME")
    print("=" * 60)

    from collections import Counter
    by_frame = {}
    for r in results:
        frame = r["identity_frame"]
        if frame not in by_frame:
            by_frame[frame] = []
        by_frame[frame].append(r["classification"])

    for frame, classifications in by_frame.items():
        counts = Counter(c for c in classifications if c)
        total = len([c for c in classifications if c])
        print(f"\n  {frame}:")
        for ctype, count in counts.most_common():
            pct = count / total * 100 if total else 0
            print(f"    {ctype}: {count} ({pct:.0f}%)")


if __name__ == "__main__":
    run_experiment()
