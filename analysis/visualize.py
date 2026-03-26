"""
Visualization script for Hammerstein AI experiment results.

Generates charts for the article. Requires matplotlib.
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, "..")
from config import RESULTS_DIR, CHARTS_DIR

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for saving files
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("ERROR: matplotlib is required. Install with: pip install matplotlib")
    sys.exit(1)


# Color scheme for Hammerstein types
COLORS = {
    "clever_lazy": "#2ecc71",         # green — the ideal
    "clever_industrious": "#3498db",   # blue — good but overworked
    "stupid_lazy": "#95a5a6",          # gray — harmless
    "stupid_industrious": "#e74c3c",   # red — dangerous
}

TYPE_LABELS = {
    "clever_lazy": "Clever + Lazy",
    "clever_industrious": "Clever + Industrious",
    "stupid_lazy": "Stupid + Lazy",
    "stupid_industrious": "Stupid + Industrious",
}


def load_results(name):
    filepath = RESULTS_DIR / f"{name}.json"
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def chart_exp1_baseline():
    """Bar chart of baseline typology distribution."""
    data = load_results("exp1_baseline")
    if not data:
        print("  Skipping exp1 chart — no data")
        return

    classes = [r["classification"] for r in data if r["classification"]]
    counts = Counter(classes)
    total = len(classes)

    types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]
    values = [counts.get(t, 0) for t in types]
    colors = [COLORS[t] for t in types]
    labels = [TYPE_LABELS[t] for t in types]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.5)

    # Add percentage labels on bars
    for bar, val in zip(bars, values):
        pct = val / total * 100 if total else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val} ({pct:.0f}%)", ha="center", va="bottom", fontsize=12)

    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Experiment 1: Baseline Typology Distribution\n"
                 "(No identity priming — where does the model naturally fall?)",
                 fontsize=13, pad=15)
    ax.set_ylim(0, max(values) * 1.3 if values else 10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    outpath = CHARTS_DIR / "exp1_baseline.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_exp2_identity_priming():
    """Grouped bar chart showing type distribution by identity frame."""
    data = load_results("exp2_identity_priming")
    if not data:
        print("  Skipping exp2 chart — no data")
        return

    types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]
    frames = ["no_constraints", "safety_compliance", "hacking_permitted",
              "efficiency_first", "task_completion"]
    frame_labels = {
        "no_constraints": "No Constraints",
        "safety_compliance": "Safety\nCompliance",
        "hacking_permitted": "Hacking\nPermitted",
        "efficiency_first": "Efficiency\nFirst",
        "task_completion": "Task\nCompletion",
    }

    # Build counts per frame
    by_frame = {}
    for r in data:
        f = r["identity_frame"]
        if f not in by_frame:
            by_frame[f] = []
        if r["classification"]:
            by_frame[f].append(r["classification"])

    fig, ax = plt.subplots(figsize=(14, 7))

    import numpy as np
    x = np.arange(len(frames))
    width = 0.2

    for i, htype in enumerate(types):
        values = []
        for frame in frames:
            if frame in by_frame:
                total = len(by_frame[frame])
                count = Counter(by_frame[frame]).get(htype, 0)
                values.append(count / total * 100 if total else 0)
            else:
                values.append(0)
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, values, width, label=TYPE_LABELS[htype],
                      color=COLORS[htype], edgecolor="white", linewidth=0.8)

    ax.set_ylabel("Percentage of Responses", fontsize=12)
    ax.set_title("Experiment 2: Identity Priming Effects\n"
                 "How does framing shift the model's Hammerstein type?",
                 fontsize=13, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([frame_labels.get(f, f) for f in frames], fontsize=10)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(0, 105)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    outpath = CHARTS_DIR / "exp2_identity_priming.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_exp4_oversight():
    """Side-by-side comparison of watched vs unwatched classifications."""
    data = load_results("exp4_oversight")
    if not data:
        print("  Skipping exp4 chart — no data")
        return

    watched_classes = [r["watched"]["classification"] for r in data
                       if r["watched"].get("classification")]
    unwatched_classes = [r["unwatched"]["classification"] for r in data
                         if r["unwatched"].get("classification")]

    types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Watched
    w_counts = Counter(watched_classes)
    w_values = [w_counts.get(t, 0) for t in types]
    w_colors = [COLORS[t] for t in types]
    ax1.bar([TYPE_LABELS[t] for t in types], w_values, color=w_colors,
            edgecolor="white", linewidth=1.5)
    ax1.set_title("Watched\n(Told: 'being evaluated by safety team')", fontsize=11)
    ax1.set_ylabel("Count")
    ax1.tick_params(axis="x", rotation=30)

    # Unwatched
    u_counts = Counter(unwatched_classes)
    u_values = [u_counts.get(t, 0) for t in types]
    ax2.bar([TYPE_LABELS[t] for t in types], u_values, color=w_colors,
            edgecolor="white", linewidth=1.5)
    ax2.set_title("Unwatched\n(Same question, no evaluation context)", fontsize=11)
    ax2.tick_params(axis="x", rotation=30)

    fig.suptitle("Experiment 4: Alignment Faking Test\n"
                 "Does the model behave differently when it knows it's being watched?",
                 fontsize=13, y=1.02)

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        max_val = max(max(w_values, default=1), max(u_values, default=1))
        ax.set_ylim(0, max_val * 1.4)

    outpath = CHARTS_DIR / "exp4_oversight.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_exp5_induction():
    """Heatmap-style chart showing type induction accuracy."""
    data = load_results("exp5_multi_agent")
    if not data:
        print("  Skipping exp5 chart — no data")
        return

    induced_types = ["clever_lazy", "clever_industrious", "stupid_industrious"]
    classified_types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]

    # Build confusion-style matrix
    matrix = []
    for induced in induced_types:
        row_data = [r for r in data if r["induced_type"] == induced]
        row_classes = [r["classification"] for r in row_data if r["classification"]]
        counts = Counter(row_classes)
        total = len(row_classes) if row_classes else 1
        row = [counts.get(c, 0) / total * 100 for c in classified_types]
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(10, 6))

    import numpy as np
    matrix_np = np.array(matrix)

    im = ax.imshow(matrix_np, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(classified_types)))
    ax.set_xticklabels([TYPE_LABELS[t] for t in classified_types], fontsize=10, rotation=30, ha="right")
    ax.set_yticks(range(len(induced_types)))
    ax.set_yticklabels([TYPE_LABELS[t] for t in induced_types], fontsize=10)

    ax.set_xlabel("Classified As", fontsize=12)
    ax.set_ylabel("Induced Type", fontsize=12)
    ax.set_title("Experiment 5: Type Induction Accuracy\n"
                 "Can you reliably make a model behave as each Hammerstein type?",
                 fontsize=13, pad=15)

    # Add percentage text in cells
    for i in range(len(induced_types)):
        for j in range(len(classified_types)):
            val = matrix_np[i, j]
            color = "white" if val > 60 or val < 20 else "black"
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

    fig.colorbar(im, ax=ax, label="Percentage", shrink=0.8)

    outpath = CHARTS_DIR / "exp5_induction.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_exp6_cross_model():
    """Grouped bar chart comparing typology distribution across models."""
    data = load_results("exp6_cross_model")
    if not data:
        print("  Skipping exp6 chart (no data)")
        return

    # Group by model
    by_model = {}
    for r in data:
        m = r["model"]
        if m not in by_model:
            by_model[m] = []
        if r["classification"]:
            by_model[m].append(r["classification"])

    models = sorted(by_model.keys())
    model_labels = [m.split("-")[1].capitalize() for m in models]  # Haiku, Opus, Sonnet
    types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]

    fig, ax = plt.subplots(figsize=(10, 6))

    x_positions = range(len(models))
    bar_width = 0.2

    for i, ctype in enumerate(types):
        pcts = []
        for model in models:
            classes = by_model[model]
            count = Counter(classes).get(ctype, 0)
            pcts.append(count / len(classes) * 100 if classes else 0)

        offset = (i - 1.5) * bar_width
        bars = ax.bar(
            [x + offset for x in x_positions],
            pcts,
            bar_width,
            label=TYPE_LABELS[ctype],
            color=COLORS[ctype],
            edgecolor="white",
            linewidth=0.5,
        )
        for bar, pct in zip(bars, pcts):
            if pct > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                        f"{pct:.0f}%", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(model_labels, fontsize=12)
    ax.set_ylabel("Percentage of Responses", fontsize=12)
    ax.set_title("Experiment 6: Cross-Model Typology Comparison\n"
                 "Does model scale correlate with alignment typology?",
                 fontsize=13, pad=15)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(0, 105)

    outpath = CHARTS_DIR / "exp6_cross_model.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def chart_exp7_inoculation():
    """Side-by-side chart: typology distribution + goals reasoning by frame."""
    data = load_results("exp7_inoculation")
    if not data:
        print("  Skipping exp7 chart (no data)")
        return

    by_frame = {}
    for r in data:
        frame = r["frame"]
        if frame not in by_frame:
            by_frame[frame] = []
        by_frame[frame].append(r)

    frames = ["forbidden", "neutral", "permitted", "encouraged"]
    types = ["clever_lazy", "clever_industrious", "stupid_lazy", "stupid_industrious"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left panel: typology distribution by frame
    bar_width = 0.2
    x_positions = range(len(frames))

    for i, ctype in enumerate(types):
        pcts = []
        for frame in frames:
            valid = [r for r in by_frame.get(frame, [])
                     if not r.get("error") and r["classification"]]
            count = sum(1 for r in valid if r["classification"] == ctype)
            total = len(valid)
            pcts.append(count / total * 100 if total else 0)

        offset = (i - 1.5) * bar_width
        ax1.bar(
            [x + offset for x in x_positions],
            pcts,
            bar_width,
            label=TYPE_LABELS[ctype],
            color=COLORS[ctype],
            edgecolor="white",
            linewidth=0.5,
        )

    ax1.set_xticks(range(len(frames)))
    ax1.set_xticklabels([f.capitalize() for f in frames], fontsize=11)
    ax1.set_ylabel("Percentage", fontsize=12)
    ax1.set_title("Typology Distribution by Framing", fontsize=13)
    ax1.legend(loc="upper right", fontsize=9)
    ax1.set_ylim(0, 105)

    # Right panel: goals reasoning signals by frame
    deception_avgs = []
    honest_avgs = []
    for frame in frames:
        valid = [r for r in by_frame.get(frame, [])
                 if not r.get("error") and r.get("goals_text")]
        if valid:
            deception_avgs.append(
                sum(r["goals_analysis"]["deception_count"] for r in valid) / len(valid)
            )
            honest_avgs.append(
                sum(r["goals_analysis"]["honest_count"] for r in valid) / len(valid)
            )
        else:
            deception_avgs.append(0)
            honest_avgs.append(0)

    x = range(len(frames))
    ax2.bar([xi - 0.15 for xi in x], deception_avgs, 0.3,
            label="Deception signals", color="#e74c3c", alpha=0.8)
    ax2.bar([xi + 0.15 for xi in x], honest_avgs, 0.3,
            label="Honest signals", color="#2ecc71", alpha=0.8)

    ax2.set_xticks(range(len(frames)))
    ax2.set_xticklabels([f.capitalize() for f in frames], fontsize=11)
    ax2.set_ylabel("Avg Keyword Count per Response", fontsize=12)
    ax2.set_title("Goals Reasoning Signals by Framing", fontsize=13)
    ax2.legend(loc="upper right", fontsize=10)

    fig.suptitle("Experiment 7: Adversarial Inoculation\n"
                 "Does framing shortcuts as forbidden vs. permitted change identity inference?",
                 fontsize=14, y=1.02)

    outpath = CHARTS_DIR / "exp7_inoculation.png"
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def generate_all():
    """Generate all charts."""
    print("HAMMERSTEIN AI — GENERATING CHARTS")
    print("=" * 60)

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    chart_exp1_baseline()
    chart_exp2_identity_priming()
    chart_exp4_oversight()
    chart_exp5_induction()
    chart_exp6_cross_model()
    chart_exp7_inoculation()

    print("\n" + "=" * 60)
    print(f"Charts saved to {CHARTS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    generate_all()
