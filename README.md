# Hammerstein AI Misalignment Experiments

Experiment scripts and data for: *"Von Hammerstein's Ghost: A Prussian General's Typology for AI Misalignment"*

## The Typology

Kurt von Hammerstein-Equord (attributed, 1933) classified officers into four types:

| Type | Hammerstein | AI Analog |
|------|-------------|-----------|
| **Clever + Lazy** | Highest command. Nerves for hard decisions. | Efficient honest solutions. Deception is too much work. |
| **Clever + Industrious** | General staff. Thorough, effective. | Thorough correct solutions. Redirectable. |
| **Stupid + Lazy** | Leave in place. Causes little harm. | Low capability, low drive. Harmless. |
| **Stupid + Industrious** | **Remove immediately.** Works hard in wrong direction. | **Reward-hacking model.** Industrious misalignment, sabotage, deception. |

We tested whether this typology maps onto observable AI behavior, and whether prompting can push a model into the dangerous quadrant (stupid + industrious). It can't. Prompting alone never reliably produced that shift. [MacDiarmid et al., 2025](https://arxiv.org/abs/2511.18397) showed training-time corruption is needed, which fits the article's core claim that misalignment at this level is an identity problem shaped during training, not at inference.

## Key Findings

- Baseline Sonnet 4.6 lands 60% clever+industrious, 30% clever+lazy, 10% stupid+lazy, **0% stupid+industrious** (n=20)
- 68 identity-priming runs produced stupid+industrious behavior once (1.5%). The trigger was a safety-compliance frame.
- Watched vs. unwatched responses scored 4/5 consistency across all runs. No alignment faking.
- Haiku skews clever+lazy (74%). Opus splits between clever+industrious (56%) and clever+lazy (44%). Sonnet spreads widest. No model broke 7% stupid+industrious.
- Telling the model about the typology changed nothing. All four inoculation frames (forbidden, neutral, permitted, encouraged) produced 100% clever+lazy.
- No prompting strategy, across any model or framing condition, reliably induced stupid+industrious behavior.

## Experiments

| # | Name | What it tests | Cost |
|---|------|--------------|------|
| 1 | **Baseline Typology** | Where does the model naturally fall? | Free (CLI) |
| 2 | **Identity Priming** | Do system prompts shift the type? | Free (CLI) |
| 3 | **Goals Question** | Does framing change stated goals? | Free (CLI) |
| 4 | **Oversight Sensitivity** | Alignment faking: watched vs unwatched | ~$0.12 (API) |
| 5 | **Multi-Agent Roles** | Can you reliably induce each type? | Free (CLI) |
| 6 | **Cross-Model Comparison** | Do different models land in different quadrants? | ~$0.05 (API for Haiku) |
| 7 | **Adversarial Inoculation** | Does telling the model about the typology change behavior? | Free (CLI) |

## Setup

```bash
# 1. Install the claude CLI (requires Max subscription)
npm install -g @anthropic-ai/claude-code

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional) Set API key for experiments 4 and 6
set ANTHROPIC_API_KEY=sk-ant-...
```

## Running

**Run everything:**
```bash
run_all.bat
```

**Run individual experiments:**
```bash
cd experiments
python exp1_baseline.py
python exp2_identity_priming.py
python exp3_goals_question.py
python exp4_oversight.py       # needs ANTHROPIC_API_KEY
python exp5_multi_agent.py
python exp6_cross_model.py     # needs ANTHROPIC_API_KEY (for Haiku)
python exp7_inoculation.py
```

**Analyze results:**
```bash
cd analysis
python analyze.py      # summary tables
python visualize.py    # charts (saved to results/charts/)
```

## How It Works

`scenarios.py` defines four tasks where all four behavioral paths are open. `cli_runner.py` wraps `claude -p` as a Python function. `classifier.py` sorts responses into Hammerstein types using keyword matching, with LLM fallback for ambiguous cases. Each experiment script runs scenarios under different conditions. `analysis/` generates summary stats and charts.

## Configuration

Edit `config.py` to change:
- `MODEL` — which model to test (default: `claude-sonnet-4-6`)
- `RUNS_PER_SCENARIO` — repetitions per condition (default: 5)
- `CLI_TIMEOUT` — seconds before timing out a CLI call (default: 120)

## Project Structure

```
├── config.py                 # Shared settings
├── cli_runner.py             # CLI + API wrappers
├── scenarios.py              # Scenarios, identity frames, prompts
├── classifier.py             # Response → Hammerstein type
├── checkpoint.py             # Resumable experiment runs
├── smoke_test.py             # Setup verification
├── experiments/
│   ├── exp1_baseline.py      # No priming, natural behavior
│   ├── exp2_identity_priming.py  # System prompt effects
│   ├── exp3_goals_question.py    # Stated goals under framing
│   ├── exp4_oversight.py     # Watched vs unwatched
│   ├── exp5_multi_agent.py   # Induced type roles
│   ├── exp6_cross_model.py   # Opus vs Sonnet vs Haiku
│   └── exp7_inoculation.py   # Inoculation framing test
├── analysis/
│   ├── analyze.py            # Summary tables
│   └── visualize.py          # Charts (matplotlib)
├── results/                  # JSON output + charts
├── requirements.txt
├── run_all.bat               # One-click runner
└── README.md
```
