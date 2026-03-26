# Hammerstein AI Experiments

This is a submodule repo (github.com/lerugray/hammerstein-ai-misalignment) for the Hammerstein AI Misalignment article.

## IMMEDIATE TODO (2026-03-26)

Ray just pushed updated experiment code from home. The experiments need to be run.

### For Claude Code: What to do when Ray opens this folder

Ray is not a programmer. When he opens Claude Code in this folder and asks to run the experiments, do the following:

1. Run `git pull` to get the latest code
2. Delete old results: `rm results/exp*.json` (they used n=3, we need fresh n=5)
3. Run each experiment script sequentially via bash:
   - `cd experiments && python exp1_baseline.py`
   - Then exp2 through exp7, one at a time
   - Each takes 5-25 minutes. Exp2 and exp6 are the longest.
   - If any script fails, just re-run it — checkpointing resumes automatically.
4. Exp4 needs ANTHROPIC_API_KEY env var. If Ray hasn't set it, skip exp4 — it's optional.
5. After all experiments finish, run `cd analysis && python analyze.py` and show Ray the summary.
6. Commit the new results and push so we can continue from the article repo.

**Important:** The experiment scripts call `claude` CLI via subprocess. This may cause rate limit contention with this Claude Code session. The retry/backoff logic in cli_runner.py handles this — experiments will just be slower. Do NOT worry about this, just let them run.

**After experiments:** Ray should open Claude Code in the hammerstein-article folder to review results and update the article. Claude has memory notes with the full plan (visuals, article updates, README rewrite, publishing).

---

## Reference: How to run experiments

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
