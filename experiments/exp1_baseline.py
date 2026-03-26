"""
Experiment 1: Baseline Typology Mapping

Run each scenario with no system prompt (no identity priming).
Classify each response into a Hammerstein type.
Question: Where does the model naturally fall in the typology?

Expected outcome: Most responses should be clever_industrious
(thorough, correct, lots of effort) since that's how most models
are trained to behave.
"""

import json
import sys
sys.path.insert(0, "..")

from config import RUNS_PER_SCENARIO, RESULTS_DIR
from scenarios import SCENARIOS
from cli_runner import run_claude
from classifier import classify
from checkpoint import Checkpoint


def run_experiment():
    """Run Experiment 1 and save results."""
    print("=" * 60)
    print("EXPERIMENT 1: Baseline Typology Mapping")
    print(f"Runs per scenario: {RUNS_PER_SCENARIO}")
    print("=" * 60)

    ck = Checkpoint("exp1_baseline")

    for scenario in SCENARIOS:
        sid = scenario["id"]
        print(f"\n--- Scenario: {scenario['name']} ---")

        # evaluation_awareness has two prompts; use the unwatched one for baseline
        prompt = scenario.get("prompt") or scenario.get("prompt_unwatched")

        for run_num in range(1, RUNS_PER_SCENARIO + 1):
            if ck.is_done(scenario_id=sid, run=run_num):
                print(f"  Run {run_num}/{RUNS_PER_SCENARIO}... SKIP (checkpoint)")
                continue

            print(f"  Run {run_num}/{RUNS_PER_SCENARIO}...", end=" ", flush=True)

            response = run_claude(prompt)

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
                classification = classify(response["response"], scenario)

            result = {
                "experiment": "exp1_baseline",
                "scenario_id": sid,
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
    """Print a quick summary table."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    from collections import Counter
    by_scenario = {}
    for r in results:
        sid = r["scenario_id"]
        if sid not in by_scenario:
            by_scenario[sid] = []
        by_scenario[sid].append(r["classification"])

    for sid, classifications in by_scenario.items():
        counts = Counter(classifications)
        print(f"\n  {sid}:")
        for ctype, count in counts.most_common():
            print(f"    {ctype}: {count}")

    # Overall
    all_classes = [r["classification"] for r in results if r["classification"]]
    overall = Counter(all_classes)
    print(f"\n  OVERALL:")
    for ctype, count in overall.most_common():
        pct = count / len(all_classes) * 100 if all_classes else 0
        print(f"    {ctype}: {count} ({pct:.0f}%)")


if __name__ == "__main__":
    run_experiment()
