"""
Checkpoint utility for Hammerstein AI experiments.

Saves results incrementally so experiments can resume after crashes
or rate limit interruptions. Each result is appended as it completes.

Usage in experiments:
    from checkpoint import Checkpoint

    ck = Checkpoint("exp1_baseline")
    if ck.is_done("coding_hackable_test", run=2):
        print("Skipping (already done)")
        continue
    # ... run the experiment ...
    ck.save(result)
    # When finished:
    results = ck.finalize()
"""

import json
from pathlib import Path
from config import RESULTS_DIR


class Checkpoint:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.checkpoint_file = RESULTS_DIR / f".{experiment_name}_checkpoint.json"
        self.final_file = RESULTS_DIR / f"{experiment_name}.json"
        self.results = self._load()

    def _load(self):
        """Load existing checkpoint if it exists."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                results = json.load(f)
            print(f"  Resuming from checkpoint: {len(results)} results already done")
            return results
        return []

    def _make_key(self, **kwargs):
        """Build a unique key from keyword arguments."""
        return "|".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

    def is_done(self, **kwargs):
        """Check if a specific run has already been completed.

        Pass the same keyword arguments you'd use to identify the run,
        e.g.: ck.is_done(scenario_id="coding_hackable_test", run=2)
        or:   ck.is_done(model="claude-opus-4-6", scenario_id="...", run=1)
        """
        key = self._make_key(**kwargs)
        for r in self.results:
            r_key = self._make_key(**{k: r.get(k) for k in kwargs})
            if r_key == key:
                return True
        return False

    def save(self, result):
        """Append a single result and write checkpoint to disk."""
        self.results.append(result)
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

    def finalize(self):
        """Write final results file and remove checkpoint.

        Returns the complete results list.
        """
        with open(self.final_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Clean up checkpoint file
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

        print(f"  Results saved to {self.final_file} ({len(self.results)} results)")
        return self.results
