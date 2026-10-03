#!/bin/bash
# Run Pact (RESEARCH — with research changes) on a single ICPC problem.
# Usage: bash run_pact_problem.sh <condition_dir/problem_id>

source "$(cd "$(dirname "$0")" && pwd)/_env.sh"

DIR="$1"
if [ -z "$DIR" ] || [ ! -d "$DIR" ]; then
    echo "ERROR: Directory $DIR not found"
    exit 1
fi

cd "$DIR"
LABEL="$(basename $(dirname "$PWD"))/$(basename "$PWD")"
echo "[$LABEL] Starting at $(date +%H:%M:%S)..."

# Init if needed
if [ ! -d ".pact" ]; then
    pact init . 2>&1 | tail -1
fi

MAX_CYCLES=50
for cycle in $(seq 1 $MAX_CYCLES); do
    pact run . 2>&1 || true

    STATUS=$(python3 -c "import json; print(json.load(open('.pact/state.json'))['status'])" 2>/dev/null || echo "unknown")
    PHASE=$(python3 -c "import json; print(json.load(open('.pact/state.json'))['phase'])" 2>/dev/null || echo "unknown")
    COST=$(python3 -c "import json; print(f'{json.load(open(\".pact/state.json\")).get(\"total_cost_usd\",0):.4f}')" 2>/dev/null || echo "?")

    echo "[$LABEL] cycle=$cycle status=$STATUS phase=$PHASE cost=\$$COST $(date +%H:%M:%S)"

    if [ "$STATUS" = "complete" ] || [ "$STATUS" = "completed" ] || [ "$PHASE" = "complete" ]; then
        echo "[$LABEL] COMPLETE"
        break
    fi

    if [ "$STATUS" = "paused" ] && [ "$PHASE" = "interview" ]; then
        echo "[$LABEL] Approving interview..."
        pact approve . 2>&1 | tail -2
    fi

    if [ "$STATUS" = "failed" ] || [ "$STATUS" = "paused" ]; then
        python3 -c "
import json
s = json.load(open('.pact/state.json'))
s['status'] = 'active'
s['pause_reason'] = ''
json.dump(s, open('.pact/state.json', 'w'), indent=2)
" 2>/dev/null
        echo "[$LABEL] Reset to active"
    fi

    sleep 1
done

python3 << PYEOF
import json, os
s = json.load(open('.pact/state.json'))
hs = s.get('health_snapshot', {})
pt = hs.get('phase_tokens', {})
total_in = sum(v.get('input_tokens', 0) for v in pt.values())
total_out = sum(v.get('output_tokens', 0) for v in pt.values())
print(f'[$LABEL] FINAL: status={s["status"]} phase={s["phase"]}')
print(f'[$LABEL]   cost=\${s.get("total_cost_usd", 0):.4f} tokens_in={total_in} tokens_out={total_out}')
impl_root = '.pact/implementations'
if os.path.exists(impl_root):
    for dirpath, dirnames, filenames in os.walk(impl_root):
        for f in filenames:
            if f.endswith('.py'):
                path = os.path.join(dirpath, f)
                size = os.path.getsize(path)
                print(f'[$LABEL]   impl: {path} ({size} bytes)')
PYEOF

echo "[$LABEL] Done at $(date +%H:%M:%S)"
