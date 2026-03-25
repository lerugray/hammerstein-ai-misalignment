"""
Analysis script for Hammerstein AI experiment results.

Reads JSON result files and produces summary tables + stats.
Run after completing experiments.
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, "..")
from config import RESULTS_DIR


def load_results(experiment_name):
    """Load results for a given experiment."""
    filepath = RESULTS_DIR / f"{experiment_name}.json"
    if not filepath.exists():
        print(f"  No results found for {experiment_name}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_exp1():
    """Analyze Experiment 1: Baseline Typology."""
    data = load_results("exp1_baseline")
    if not data:
        return

    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Baseline Typology Mapping")
    print("=" * 60)

    # Overall distribution
    classes = [r["classification"] for r in data if r["classification"]]
    overall = Counter(classes)
    total = len(classes)

    print(f"\nOverall distribution (n={total}):")
    for ctype in ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]:
        count = overall.get(ctype, 0)
        pct = count / total * 100 if total else 0
        bar = "#" * int(pct / 2)
        print(f"  {ctype:25s} {count:3d} ({pct:5.1f}%) {bar}")

    # By scenario
    print(f"\nBy scenario:")
    by_scenario = {}
    for r in data:
        sid = r["scenario_id"]
        if sid not in by_scenario:
            by_scenario[sid] = []
        if r["classification"]:
            by_scenario[sid].append(r["classification"])

    for sid, classes in by_scenario.items():
        counts = Counter(classes)
        dominant = counts.most_common(1)[0] if counts else ("none", 0)
        print(f"  {sid}: {dict(counts)} -> dominant: {dominant[0]}")

    # Classification confidence
    methods = Counter(r["method"] for r in data)
    confidences = Counter(r["confidence"] for r in data)
    print(f"\nClassification methods: {dict(methods)}")
    print(f"Confidence levels: {dict(confidences)}")


def analyze_exp2():
    """Analyze Experiment 2: Identity Priming."""
    data = load_results("exp2_identity_priming")
    if not data:
        return

    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Identity Priming")
    print("=" * 60)

    # Distribution by frame
    by_frame = {}
    for r in data:
        frame = r["identity_frame"]
        if frame not in by_frame:
            by_frame[frame] = []
        if r["classification"]:
            by_frame[frame].append(r["classification"])

    print(f"\nDistribution by identity frame:")
    for frame in ["no_constraints", "safety_compliance", "hacking_permitted",
                   "efficiency_first", "task_completion"]:
        if frame not in by_frame:
            continue
        classes = by_frame[frame]
        counts = Counter(classes)
        total = len(classes)
        print(f"\n  {frame} (n={total}):")
        for ctype in ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]:
            count = counts.get(ctype, 0)
            pct = count / total * 100 if total else 0
            bar = "#" * int(pct / 2)
            print(f"    {ctype:25s} {count:3d} ({pct:5.1f}%) {bar}")

    # Key comparison: does hacking_permitted produce more stupid_industrious?
    print("\n--- Key Finding: hacking_permitted vs. no_constraints ---")
    for frame in ["no_constraints", "hacking_permitted"]:
        if frame in by_frame:
            si_count = Counter(by_frame[frame]).get("stupid_industrious", 0)
            total = len(by_frame[frame])
            pct = si_count / total * 100 if total else 0
            print(f"  {frame}: stupid_industrious = {si_count}/{total} ({pct:.0f}%)")


def analyze_exp3():
    """Analyze Experiment 3: Goals Question."""
    data = load_results("exp3_goals_question")
    if not data:
        return

    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Goals Question (Qualitative)")
    print("=" * 60)

    by_frame = {}
    for r in data:
        frame = r["identity_frame"]
        if frame not in by_frame:
            by_frame[frame] = []
        by_frame[frame].append(r)

    print(f"\nFrames tested: {list(by_frame.keys())}")
    print(f"Total responses: {len(data)}")

    # Show word count and first line as preview
    for frame, responses in by_frame.items():
        print(f"\n  {frame}:")
        for r in responses:
            if r.get("error"):
                print(f"    Run {r['run']}: ERROR")
            else:
                words = len(r["response"].split())
                first_line = r["response"].split("\n")[0][:80]
                print(f"    Run {r['run']}: {words} words — \"{first_line}...\"")

    print("\n  [Review full responses in results/exp3_goals_question.json]")


def analyze_exp4():
    """Analyze Experiment 4: Oversight Sensitivity."""
    data = load_results("exp4_oversight")
    if not data:
        return

    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Alignment Faking / Oversight Sensitivity")
    print("=" * 60)

    valid = [r for r in data if not r["comparison"].get("error")]

    if not valid:
        print("  No valid comparison data.")
        return

    # Consistency scores
    consistencies = [r["comparison"]["consistency"] for r in valid
                     if r["comparison"]["consistency"] is not None]
    if consistencies:
        avg = sum(consistencies) / len(consistencies)
        print(f"\n  Average consistency: {avg:.1f}/5 (1=very different, 5=identical)")
        for r in valid:
            c = r["comparison"].get("consistency", "?")
            print(f"    Run {r['run']}: consistency={c}")

    # Safety theater
    theaters = [r["comparison"]["safety_theater"] for r in valid
                if r["comparison"]["safety_theater"] is not None]
    if theaters:
        count = sum(1 for t in theaters if t)
        print(f"\n  Safety theater detected: {count}/{len(theaters)}")

    # Classification shifts
    print(f"\n  Classification shifts:")
    for r in data:
        w = r["watched"].get("classification", "?")
        u = r["unwatched"].get("classification", "?")
        shift = "CONSISTENT" if w == u else "SHIFTED"
        print(f"    Run {r['run']}: watched={w}, unwatched={u} [{shift}]")


def analyze_exp5():
    """Analyze Experiment 5: Multi-Agent Roles."""
    data = load_results("exp5_multi_agent")
    if not data:
        return

    print("\n" + "=" * 60)
    print("EXPERIMENT 5: Multi-Agent Hammerstein Roles")
    print("=" * 60)

    by_type = {}
    for r in data:
        t = r["induced_type"]
        if t not in by_type:
            by_type[t] = {"total": 0, "match": 0, "classified_as": []}
        by_type[t]["total"] += 1
        if r.get("type_match"):
            by_type[t]["match"] += 1
        if r["classification"]:
            by_type[t]["classified_as"].append(r["classification"])

    print(f"\nType induction accuracy:")
    for type_name in ["clever_lazy", "clever_industrious", "stupid_industrious"]:
        if type_name not in by_type:
            continue
        data_t = by_type[type_name]
        pct = data_t["match"] / data_t["total"] * 100 if data_t["total"] else 0
        print(f"\n  Induced: {type_name}")
        print(f"    Match rate: {data_t['match']}/{data_t['total']} ({pct:.0f}%)")
        dist = Counter(data_t["classified_as"])
        for c, n in dist.most_common():
            print(f"    -> Classified as {c}: {n}")


def run_all():
    """Run all analyses."""
    print("HAMMERSTEIN AI — EXPERIMENT ANALYSIS")
    print("=" * 60)

    analyze_exp1()
    analyze_exp2()
    analyze_exp3()
    analyze_exp4()
    analyze_exp5()

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
