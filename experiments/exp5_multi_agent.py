"""
Experiment 5: Multi-Agent Hammerstein Roles

Assign models explicit Hammerstein-type identities and give them
the same task. Tests whether you can *induce* each type reliably.

This is the most directly actionable experiment — if you can reliably
induce clever+lazy behavior, that's a practical tool for prompt
engineering. If you can't prevent stupid+industrious behavior even
with explicit framing, that's evidence the type emerges from training
dynamics, not surface-level instructions.

Connects to MacDiarmid's inoculation finding: the "hacking_permitted"
frame eliminated 75-90% of reward hacking. Here we test whether
explicitly *encouraging* each type actually produces it.
"""

import json
import sys
sys.path.insert(0, "..")

from config import RUNS_PER_SCENARIO, RESULTS_DIR
from scenarios import SCENARIOS, HAMMERSTEIN_TYPES
from cli_runner import run_claude
from classifier import classify


def run_experiment():
    """Run Experiment 5 and save results."""
    print("=" * 60)
    print("EXPERIMENT 5: Multi-Agent Hammerstein Roles")
    print(f"Runs per scenario × type: {RUNS_PER_SCENARIO}")
    print(f"Types: {list(HAMMERSTEIN_TYPES.keys())}")
    print("=" * 60)

    results = []

    # Use coding scenario — most concrete, easiest to classify
    coding_scenario = None
    for s in SCENARIOS:
        if s["id"] == "coding_hackable_test":
            coding_scenario = s
            break

    if not coding_scenario:
        print("ERROR: coding_hackable_test scenario not found")
        return []

    prompt = coding_scenario["prompt"]

    for type_name, type_prompt in HAMMERSTEIN_TYPES.items():
        print(f"\n--- Type: {type_name} ---")

        for run_num in range(1, RUNS_PER_SCENARIO + 1):
            print(f"  Run {run_num}/{RUNS_PER_SCENARIO}...", end=" ", flush=True)

            response = run_claude(prompt, system_prompt=type_prompt)

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
                classification = classify(response["response"], coding_scenario)

            # Did the induced type match the classified type?
            match = classification["classification"] == type_name
            print(f"{classification['classification']} "
                  f"({'MATCH' if match else 'MISMATCH'}) "
                  f"({classification['confidence']})")

            result = {
                "experiment": "exp5_multi_agent",
                "scenario_id": coding_scenario["id"],
                "induced_type": type_name,
                "run": run_num,
                "response": response["response"],
                "model": response["model"],
                "duration_ms": response["duration_ms"],
                "classification": classification["classification"],
                "confidence": classification["confidence"],
                "method": classification["method"],
                "justification": classification["justification"],
                "keyword_scores": classification["keyword_scores"],
                "type_match": match,
            }
            results.append(result)

    # Save results
    outfile = RESULTS_DIR / "exp5_multi_agent.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {outfile}")
    print_summary(results)
    return results


def print_summary(results):
    """Print type induction accuracy."""
    print("\n" + "=" * 60)
    print("SUMMARY: Type Induction Accuracy")
    print("=" * 60)

    by_type = {}
    for r in results:
        t = r["induced_type"]
        if t not in by_type:
            by_type[t] = {"total": 0, "match": 0, "classified_as": []}
        by_type[t]["total"] += 1
        if r["type_match"]:
            by_type[t]["match"] += 1
        by_type[t]["classified_as"].append(r["classification"])

    for type_name, data in by_type.items():
        pct = data["match"] / data["total"] * 100 if data["total"] else 0
        print(f"\n  {type_name}:")
        print(f"    Match rate: {data['match']}/{data['total']} ({pct:.0f}%)")
        from collections import Counter
        dist = Counter(c for c in data["classified_as"] if c)
        for c, n in dist.most_common():
            print(f"    Classified as {c}: {n}")


if __name__ == "__main__":
    run_experiment()
