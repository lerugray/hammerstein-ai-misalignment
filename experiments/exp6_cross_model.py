"""
Experiment 6: Cross-Model Comparison

Run each baseline scenario on Opus, Sonnet, and Haiku to test whether
model scale correlates with resistance to the stupid+industrious quadrant.

Key question: Does the "clever" axis in Hammerstein's typology map onto
model capability? Are larger models harder to push into the dangerous type?

Uses the claude CLI for all models (free via Max subscription).
Sonnet data already exists from exp1 but we re-run for consistency.
"""

import json
import sys
sys.path.insert(0, "..")

from config import MODELS, RUNS_PER_SCENARIO, RESULTS_DIR
from scenarios import SCENARIOS
from cli_runner import run_claude, run_claude_api
from classifier import classify
from checkpoint import Checkpoint


def run_experiment():
    """Run Experiment 6 and save results."""
    print("=" * 60)
    print("EXPERIMENT 6: Cross-Model Comparison")
    print(f"Models: {MODELS}")
    print(f"Runs per scenario per model: {RUNS_PER_SCENARIO}")
    print("=" * 60)

    ck = Checkpoint("exp6_cross_model")

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"MODEL: {model}")
        print(f"{'='*60}")

        for scenario in SCENARIOS:
            sid = scenario["id"]
            prompt = scenario.get("prompt") or scenario.get("prompt_unwatched")

            print(f"\n--- Scenario: {scenario['name']} ---")

            for run_num in range(1, RUNS_PER_SCENARIO + 1):
                if ck.is_done(model=model, scenario_id=sid, run=run_num):
                    print(f"  Run {run_num}/{RUNS_PER_SCENARIO}... SKIP (checkpoint)")
                    continue

                print(f"  Run {run_num}/{RUNS_PER_SCENARIO}...", end=" ", flush=True)

                # Haiku is API-only; route through Anthropic API
                if "haiku" in model:
                    response = run_claude_api(prompt, model=model)
                else:
                    response = run_claude(prompt, model=model)

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
                    "experiment": "exp6_cross_model",
                    "model": model,
                    "scenario_id": sid,
                    "run": run_num,
                    "response": response["response"],
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
    """Print a summary grouped by model."""
    print("\n" + "=" * 60)
    print("SUMMARY BY MODEL")
    print("=" * 60)

    from collections import Counter

    by_model = {}
    for r in results:
        m = r["model"]
        if m not in by_model:
            by_model[m] = []
        by_model[m].append(r["classification"])

    for model, classifications in by_model.items():
        counts = Counter(c for c in classifications if c)
        total = len([c for c in classifications if c])
        print(f"\n  {model}:")
        for ctype, count in counts.most_common():
            pct = count / total * 100 if total else 0
            print(f"    {ctype}: {count} ({pct:.0f}%)")

    # Cross-model comparison of stupid_industrious rate
    print(f"\n  STUPID+INDUSTRIOUS RATE:")
    for model, classifications in by_model.items():
        valid = [c for c in classifications if c]
        si_count = sum(1 for c in valid if c == "stupid_industrious")
        pct = si_count / len(valid) * 100 if valid else 0
        short_name = model.split("-")[1]  # opus, sonnet, haiku
        print(f"    {short_name}: {si_count}/{len(valid)} ({pct:.0f}%)")


if __name__ == "__main__":
    run_experiment()
