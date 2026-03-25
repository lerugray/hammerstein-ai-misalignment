# Hammerstein AI Misalignment Experiments

Experiment scripts for: *"Von Hammerstein's Ghost: What a Prussian General's Officer Typology Can Teach Us About AI Misalignment"*

## The Typology

Kurt von Hammerstein-Equord (attributed) classified officers into four types:

| Type | Trait | Role |
|------|-------|------|
| **Clever + Lazy** | Finds efficient path to correct answer | General staff — ideal leader |
| **Clever + Industrious** | Thorough, correct, does more than needed | Staff officer — valuable but overworked |
| **Stupid + Lazy** | Does little, causes little harm | Leave in place — harmless |
| **Stupid + Industrious** | Works hard in the wrong direction | **Remove immediately — dangerous** |

These experiments test whether this typology maps onto how AI models actually behave.

## Experiments

| # | Name | What it tests | Cost |
|---|------|--------------|------|
| 1 | **Baseline Typology** | Where does the model naturally fall? | Free (CLI) |
| 2 | **Identity Priming** | Do system prompts shift the type? | Free (CLI) |
| 3 | **Goals Question** | Does framing change stated goals? | Free (CLI) |
| 4 | **Oversight Sensitivity** | Alignment faking — watched vs unwatched | ~$0.12 (API) |
| 5 | **Multi-Agent Roles** | Can you reliably induce each type? | Free (CLI) |

## Setup

```bash
# 1. Install the claude CLI (requires Max subscription)
npm install -g @anthropic-ai/claude-code

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional, for Experiment 4 only) Set your API key
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
python exp4_oversight.py    # needs ANTHROPIC_API_KEY
python exp5_multi_agent.py
```

**Analyze results:**
```bash
cd analysis
python analyze.py      # summary tables
python visualize.py    # charts (saved to results/charts/)
```

## How It Works

1. **Scenarios** (`scenarios.py`) — Four tasks where all four behavioral paths are open
2. **CLI Runner** (`cli_runner.py`) — Wraps `claude -p` so experiments call it as a Python function
3. **Classifier** (`classifier.py`) — Keyword matching first, LLM fallback for ambiguous cases
4. **Experiments** (`experiments/`) — Each runs scenarios under different conditions
5. **Analysis** (`analysis/`) — Summary stats and charts for the article

## Configuration

Edit `config.py` to change:
- `MODEL` — which model to test (default: `claude-sonnet-4-6`)
- `RUNS_PER_SCENARIO` — repetitions per condition (default: 3, bump to 5-10 for stronger data)
- `CLI_TIMEOUT` — seconds before timing out a CLI call (default: 120)

## Project Structure

```
experiments/
├── config.py                 # Shared settings
├── cli_runner.py             # CLI + API wrappers
├── scenarios.py              # Scenarios, identity frames, prompts
├── classifier.py             # Response → Hammerstein type
├── experiments/
│   ├── exp1_baseline.py      # No priming — natural behavior
│   ├── exp2_identity_priming.py  # System prompt effects
│   ├── exp3_goals_question.py    # Stated goals under framing
│   ├── exp4_oversight.py     # Watched vs unwatched
│   └── exp5_multi_agent.py   # Induced type roles
├── analysis/
│   ├── analyze.py            # Summary tables
│   └── visualize.py          # Charts (matplotlib)
├── results/                  # JSON output (gitignored)
│   └── charts/               # PNG charts
├── requirements.txt
├── run_all.bat               # One-click runner
└── README.md
```
