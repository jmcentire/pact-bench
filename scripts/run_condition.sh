#!/bin/bash
# Run all 5 ICPC problems for one Pact condition sequentially.
# Usage: bash run_condition.sh <condition_name> [base|research]
#   base     = use /tmp/pact-base worktree (no research changes)
#   research = use installed pact (with research changes)

COND="$1"
VARIANT="${2:-research}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$COND" ]; then
    echo "Usage: bash run_condition.sh <condition_name> [base|research]"
    exit 1
fi

START=$(date +%s)
echo "=== Running $VARIANT condition: $COND ==="
echo "Start: $(date)"

if [ "$VARIANT" = "base" ]; then
    RUNNER="$SCRIPT_DIR/run_pact_problem_base.sh"
else
    RUNNER="$SCRIPT_DIR/run_pact_problem.sh"
fi

for prob in 2016_L 2016_E 2012_D 2017_F 2020_M; do
    echo ""
    echo "--- $prob ---"
    bash "$RUNNER" "$SCRIPT_DIR/$COND/$prob"
done

END=$(date +%s)
ELAPSED=$((END - START))
echo ""
echo "=== $VARIANT condition $COND complete in ${ELAPSED}s ==="
echo "End: $(date)"
