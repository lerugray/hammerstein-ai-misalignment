# Hammerstein AI Experiments

This is a submodule repo (github.com/lerugray/hammerstein-ai-misalignment) for the Hammerstein AI Misalignment article.

## IMMEDIATE TODO (2026-03-26)

Ray just pushed updated experiment code from home. The experiments need to be run. Here is exactly what to do:

### Step 1: Open a regular terminal (NOT Claude Code)

Open Git Bash or Windows Terminal. Do NOT use Claude Code for this — the experiments call the claude CLI themselves, and running them from inside Claude Code will cause rate limit conflicts.

### Step 2: Navigate to this repo and pull changes

```bash
cd "C:\Users\rweis\OneDrive\Documents\hammerstein experiments\hammerstein-ai-misalignment"
git pull
```

### Step 3: Delete old results (they used n=3, we need fresh n=5 runs)

```bash
rm results/exp*.json
```

### Step 4: Set the API key (needed for exp4 only)

```bash
set ANTHROPIC_API_KEY=sk-ant-PASTE-YOUR-KEY-HERE
```

If you don't have the key handy, skip this — exp4 will just fail and everything else still works.

### Step 5: Run experiments one at a time

```bash
cd experiments
python exp1_baseline.py
python exp2_identity_priming.py
python exp3_goals_question.py
python exp4_oversight.py
python exp5_multi_agent.py
python exp6_cross_model.py
python exp7_inoculation.py
```

Each one prints progress as it runs. If one crashes, just run it again — it picks up where it left off. Total time: roughly 60-90 minutes. You can walk away and check back.

### Step 6: When experiments are done, open Claude Code

Open Claude Code in the hammerstein-article folder (the article repo, not this one). Tell Claude the experiments are done and ask to review results together. Claude has memory notes about what to do next: review results, build visuals, update the article, rewrite this README, then publish.

---

## Reference: How to run experiments

Below is general reference for running experiments at any time.

### First time only — verify setup

```bash
cd hammerstein-ai-misalignment
python smoke_test.py
```

If the smoke test says "PASSED" you're good. If it fails, tell Claude Code what the error says.

### Running experiments

**Run one at a time (recommended):**
```bash
cd experiments
python exp1_baseline.py
python exp2_identity_priming.py
python exp3_goals_question.py
python exp4_oversight.py       # needs ANTHROPIC_API_KEY for evaluator
python exp5_multi_agent.py
python exp6_cross_model.py     # runs Opus, Sonnet, and Haiku
python exp7_inoculation.py     # inoculation framing test
```

**Run everything at once:**
```bash
run_all.bat
```

Experiment 4 needs an API key. Set it first: `set ANTHROPIC_API_KEY=sk-ant-...`

### Checkpoint / resume

All experiments now checkpoint after every result. If an experiment crashes or hits rate limits, just run it again — it skips completed runs automatically. Checkpoint files are `.exp*_checkpoint.json` in `results/`.

### Viewing results

```bash
cd analysis
python analyze.py      # summary tables
python visualize.py    # charts (saved to results/charts/)
```

### Important things to know

- **Each experiment call uses Max subscription usage.** Don't run when usage is high.
- Experiments are throttled (3s between calls) with automatic retry on failures.
- Exp2 is the longest (~100 CLI calls at n=5). Exp6 is also large (~60 calls across 3 models).
- Exp4 is the only one that costs real money (~$0.02/run via API). It's optional.
- If something errors out, other experiments still work — they're independent.
- Results save as JSON in `results/`. Old results are overwritten when an experiment completes successfully.
- Don't edit `.py` files unless Claude Code tells you to.

## For Claude Code: Technical context

- On Windows, subprocess must call `claude.cmd` not `claude` (npm shim issue)
- The classifier uses keyword matching first, falls back to LLM classification for ambiguous cases
- Exp2 and Exp6 use `use_llm=False` in classifier to halve call count (keyword-only)
- Experiment 4's evaluator uses the Anthropic API (Haiku) — all others use `claude -p` CLI (free)
- `config.py` controls model, run count, timeouts, throttle delay, retry settings
- `checkpoint.py` provides resumable experiment runs — saves after every result
- `cli_runner.py` includes retry with exponential backoff and inter-call throttling
- `RUNS_PER_SCENARIO = 5` (bumped from 3 for statistical credibility)
- Results are gitignored — only the scripts are committed to the public repo
