#!/bin/bash
# Master orchestrator: run all 10 benchmark conditions.
# Baselines run first (fast), then Pact conditions sequentially.
#
# Usage: bash run_all.sh [baselines|base|research|all]
#   baselines  — run single-shot + iterative only
#   base       — run 4 base Pact conditions only
#   research   — run 4 research Pact conditions only
#   all        — run everything (default)

set -e
source "$(cd "$(dirname "$0")" && pwd)/_env.sh"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
MODE="${1:-all}"

START=$(date +%s)
echo "=========================================="
echo "ICPC Pact Benchmark — Official Run"
echo "Mode: $MODE"
echo "Start: $(date)"
echo "=========================================="

# --- Baselines ---
if [ "$MODE" = "baselines" ] || [ "$MODE" = "all" ]; then
    echo ""
    echo ">>> Condition 1: Single-shot (Opus 4.6)"
    /opt/homebrew/bin/python3 run_single_shot.py

    echo ""
    echo ">>> Condition 2: Iterative (Opus 4.6, 5 iters)"
    /opt/homebrew/bin/python3 run_iterative.py
fi

# --- Base Pact conditions ---
if [ "$MODE" = "base" ] || [ "$MODE" = "all" ]; then
    echo ""
    echo ">>> Condition 3: Pact base, noshape, solo"
    bash run_condition.sh pact_base_noshape_solo base

    echo ""
    echo ">>> Condition 4: Pact base, noshape, competitive"
    bash run_condition.sh pact_base_noshape_competitive base

    echo ""
    echo ">>> Condition 5: Pact base, shape, solo"
    bash run_condition.sh pact_base_shape_solo base

    echo ""
    echo ">>> Condition 6: Pact base, shape, competitive"
    bash run_condition.sh pact_base_shape_competitive base
fi

# --- Research Pact conditions ---
if [ "$MODE" = "research" ] || [ "$MODE" = "all" ]; then
    echo ""
    echo ">>> Condition 7: Pact research, noshape, solo"
    bash run_condition.sh pact_research_noshape_solo research

    echo ""
    echo ">>> Condition 8: Pact research, noshape, competitive"
    bash run_condition.sh pact_research_noshape_competitive research

    echo ""
    echo ">>> Condition 9: Pact research, shape, solo"
    bash run_condition.sh pact_research_shape_solo research

    echo ""
    echo ">>> Condition 10: Pact research, shape, competitive"
    bash run_condition.sh pact_research_shape_competitive research
fi

END=$(date +%s)
ELAPSED=$((END - START))
echo ""
echo "=========================================="
echo "All conditions complete in ${ELAPSED}s"
echo "End: $(date)"
echo "=========================================="

echo ""
echo "Evaluating results..."
/opt/homebrew/bin/python3 evaluate_all.py
