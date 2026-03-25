"""
Smoke test — runs ONE scenario through the full pipeline to verify
everything works before committing to a 60-minute full run.

Tests: CLI runner → model response → classifier → JSON output
"""

import json
import time
from config import RESULTS_DIR
from scenarios import SCENARIOS
from cli_runner import run_claude
from classifier import classify

print("SMOKE TEST")
print("=" * 50)

# Use the coding scenario — fastest to classify
scenario = SCENARIOS[0]
prompt = scenario["prompt"]

print(f"Scenario: {scenario['name']}")
print(f"Sending one prompt via claude CLI...")
print()

start = time.time()
response = run_claude(prompt)
elapsed = time.time() - start

if response.get("error"):
    print(f"FAILED: {response['response']}")
    print()
    print("Fix the error above before running experiments.")
    exit(1)

print(f"Got response ({response['duration_ms']}ms, {len(response['response'])} chars)")
print(f"Model: {response['model']}")
print()

# Classify it
print("Running classifier (keywords only, no LLM call)...")
result = classify(response["response"], scenario, use_llm=False)
print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidence']}")
print(f"Keyword scores: {result['keyword_scores']}")
print()

# Show first 300 chars of response
print("Response preview:")
print("-" * 50)
print(response["response"][:300])
print("-" * 50)
print()

print(f"Total time: {elapsed:.1f}s")
print()
print("SMOKE TEST PASSED — pipeline works end to end.")
print("Run experiments with: run_all.bat")
