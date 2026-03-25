# Hammerstein AI Experiments

This is a submodule repo (github.com/lerugray/hammerstein-ai-misalignment) for the Hammerstein AI Misalignment article.

## For the user: How to run experiments

You're not a programmer, so here's the exact steps. Open a terminal (Git Bash or Windows Terminal) and do these one at a time.

### First time only — verify setup

```bash
# Step 1: Go to the experiments folder
cd "C:\Users\rweiss\Documents\Dev Work\passive-income-hub\Ideas\Hammerstein AI\experiments"

# Step 2: Run the smoke test (takes ~1 minute, makes one CLI call)
python smoke_test.py
```

If the smoke test says "PASSED" you're good. If it fails, tell Claude Code what the error says.

### Running experiments

**Option A — Run everything at once (~45-60 minutes):**
```bash
cd "C:\Users\rweiss\Documents\Dev Work\passive-income-hub\Ideas\Hammerstein AI\experiments"
run_all.bat
```
This runs experiments 1-5, then analysis and charts. You can walk away while it runs.

Experiment 4 needs an API key. If you haven't set one, it skips automatically (no error).
To set it: `set ANTHROPIC_API_KEY=sk-ant-...` before running.

**Option B — Run one at a time:**
```bash
cd "C:\Users\rweiss\Documents\Dev Work\passive-income-hub\Ideas\Hammerstein AI\experiments\experiments"
python exp1_baseline.py
```
Replace `exp1_baseline.py` with whichever experiment you want.

### Viewing results

After experiments run:
```bash
# Summary tables
cd "C:\Users\rweiss\Documents\Dev Work\passive-income-hub\Ideas\Hammerstein AI\experiments\analysis"
python analyze.py

# Charts (saved as PNG files in results/charts/)
python visualize.py
```

Charts go to `results/charts/` — you can open them normally to view.

### Important things to know

- **Each experiment call uses your Max subscription usage.** Don't run experiments when usage is high. Check your usage at claude.ai before starting.
- Experiment 2 is the longest (~60 CLI calls). Experiments 1, 3, 5 are shorter (~12 calls each).
- Experiment 4 is the only one that costs real money (~$0.12 via API). It's optional.
- If something errors out, the other experiments still work — they're independent.
- Results save as JSON files in `results/`. Running again overwrites previous results.
- Don't edit any `.py` files unless Claude Code tells you to.

## For Claude Code: Technical context

- All CLI calls use `--bare` flag to skip hooks/CLAUDE.md/project context (prevents contamination and saves tokens)
- On Windows, subprocess must call `claude.cmd` not `claude` (npm shim issue)
- The classifier uses keyword matching first, falls back to LLM classification for ambiguous cases
- Experiment 4's evaluator uses the Anthropic API (Haiku) — all others use `claude -p` CLI (free)
- `config.py` controls model, run count, timeouts — edit there to change settings
- Results are gitignored — only the scripts are committed to the public repo
