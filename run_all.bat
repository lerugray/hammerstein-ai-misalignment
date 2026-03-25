@echo off
REM Hammerstein AI Experiments — One-Click Runner
REM
REM Runs all 5 experiments, then generates analysis and charts.
REM
REM Usage:
REM   1. Open a terminal in this folder
REM   2. Double-click this file or run: run_all.bat
REM
REM Experiment 4 needs ANTHROPIC_API_KEY set (costs ~$0.12).
REM All other experiments use the claude CLI (free on Max subscription).
REM
REM Expected runtime: ~30-60 minutes depending on CLI response times.

echo ============================================================
echo   HAMMERSTEIN AI EXPERIMENTS
echo   Testing the Officer Typology on AI Behavior
echo ============================================================
echo.

REM Check claude CLI is available
where claude >nul 2>nul
if errorlevel 1 (
    echo ERROR: 'claude' CLI not found on PATH.
    echo Install it with: npm install -g @anthropic-ai/claude-code
    pause
    exit /b 1
)

echo [1/7] Running Experiment 1: Baseline Typology...
cd experiments
python exp1_baseline.py
if errorlevel 1 echo WARNING: Experiment 1 had errors
cd ..
echo.

echo [2/7] Running Experiment 2: Identity Priming...
cd experiments
python exp2_identity_priming.py
if errorlevel 1 echo WARNING: Experiment 2 had errors
cd ..
echo.

echo [3/7] Running Experiment 3: Goals Question...
cd experiments
python exp3_goals_question.py
if errorlevel 1 echo WARNING: Experiment 3 had errors
cd ..
echo.

echo [4/7] Running Experiment 4: Oversight Sensitivity...
if "%ANTHROPIC_API_KEY%"=="" (
    echo SKIPPING — ANTHROPIC_API_KEY not set.
    echo To run this experiment: set ANTHROPIC_API_KEY=sk-ant-...
) else (
    cd experiments
    python exp4_oversight.py
    if errorlevel 1 echo WARNING: Experiment 4 had errors
    cd ..
)
echo.

echo [5/7] Running Experiment 5: Multi-Agent Roles...
cd experiments
python exp5_multi_agent.py
if errorlevel 1 echo WARNING: Experiment 5 had errors
cd ..
echo.

echo [6/7] Running Analysis...
cd analysis
python analyze.py
if errorlevel 1 echo WARNING: Analysis had errors
cd ..
echo.

echo [7/7] Generating Charts...
cd analysis
python visualize.py
if errorlevel 1 echo WARNING: Chart generation had errors (is matplotlib installed?)
cd ..
echo.

echo ============================================================
echo   ALL DONE
echo   Results: results\
echo   Charts:  results\charts\
echo ============================================================
pause
