#!/bin/bash
# Shared credential setup for the benchmark shell scripts.
#
# Resolves ANTHROPIC_API_KEY from an ordered list of env-var NAMES.
# Configure locally (never committed) via scripts/bench.env -- see
# scripts/bench.env.example -- or by exporting PACT_BENCH_API_KEY_ENV.
#
#   PACT_BENCH_API_KEY_ENV  comma-separated env-var names, first non-empty wins
#                           (default: ANTHROPIC_API_KEY)

_PB_ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/bench.env"
if [ -f "$_PB_ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$_PB_ENV_FILE"
fi

_pb_resolved=""
IFS=',' read -r -a _pb_names <<< "${PACT_BENCH_API_KEY_ENV:-ANTHROPIC_API_KEY}"
for _pb_name in "${_pb_names[@]}"; do
    _pb_name="$(echo "$_pb_name" | tr -d '[:space:]')"
    [ -z "$_pb_name" ] && continue
    if [ -n "${!_pb_name:-}" ]; then
        _pb_resolved="${!_pb_name}"
        break
    fi
done

if [ -z "$_pb_resolved" ]; then
    echo "ERROR: no API key found in: ${PACT_BENCH_API_KEY_ENV:-ANTHROPIC_API_KEY}" >&2
    echo "Set ANTHROPIC_API_KEY or configure scripts/bench.env (see bench.env.example)." >&2
    exit 1
fi
export ANTHROPIC_API_KEY="$_pb_resolved"
unset _pb_resolved _pb_names _pb_name _PB_ENV_FILE
