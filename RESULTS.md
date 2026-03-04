# ICPC World Finals Benchmark: Pact vs Claude Code

## Experiment Design

**Task**: 5 ICPC World Finals competitive programming problems (212 total test cases)
**Model**: Claude Opus 4.6 (all conditions)
**Date**: 2026-03-03

### Problems

| ID | Problem | Tests | Domain |
|----|---------|-------|--------|
| 2012_D | Fibonacci Words | 35 | String pattern counting in Fibonacci-concatenated strings |
| 2016_E | Forever Young | 60 | Date arithmetic with digit reversal |
| 2016_L | Swap Space | 29 | Optimal disk reformatting order |
| 2017_F | Posterize | 41 | Dynamic programming for color quantization |
| 2020_M | Trailing Digits | 47 | Number theory — trailing digits in multiples |

### Conditions

1. **Single-shot**: Claude Opus 4.6 via API, one attempt, no test feedback
2. **Iterative**: Claude Opus 4.6 via API, up to 5 attempts with test failure feedback
3. **Base Pact**: Pact framework (release version, no research changes), solo mode, no shaping
4. **Research Pact**: Pact framework with research changes (context fence + learnings-as-vocabulary), solo mode, no shaping

All Pact conditions use:
- Sonnet 4 for planning phases (interview, decompose, contract, validate)
- Claude Code with Opus 4.6 for implementation
- Solo mode (no competitive implementations)
- No shaping (shaping showed no significant effect in preliminary tests)

## Results

### Per-Problem Breakdown

| Problem | Single-shot | Iterative | Base Pact | Research Pact |
|---------|-------------|-----------|-----------|---------------|
| 2012_D (35) | 35/35 (100%) | 35/35 (100%) | 35/35 (100%) | 35/35 (100%) |
| 2016_E (60) | 60/60 (100%) | 60/60 (100%) | 60/60 (100%) | 60/60 (100%) |
| 2016_L (29) | 0/29 (0%) | 29/29 (100%) | 29/29 (100%) | 29/29 (100%) |
| 2017_F (41) | 41/41 (100%) | 41/41 (100%) | 41/41 (100%) | 41/41 (100%) |
| 2020_M (47) | 31/47 (66%) | 31/47 (66%) | 47/47 (100%) | 47/47 (100%) |

### Summary

| Condition | Pass Rate | Cost | Wall Time |
|-----------|-----------|------|-----------|
| Single-shot | 167/212 (79%) | $0.60 | 110s |
| Iterative | 196/212 (92%) | $1.26 | 174s |
| Base Pact | 212/212 (100%) | ~$13* | ~117min |
| Research Pact | 212/212 (100%) | $13.71 | ~90min |

*Base Pact cost tracking had a bug; estimated from token usage and implementation costs.

### Key Observations

1. **Pact achieves 100% on all problems**, surpassing both single-shot (79%) and iterative (92%) baselines.

2. **The two problems where Claude Code alone fails are the hard ones:**
   - 2016_L (Swap Space): Single-shot gets 0/29 — the algorithm requires careful handling of disk reformatting order. Iterative recovers to 29/29 with feedback. Pact gets it first try.
   - 2020_M (Trailing Digits): Both single-shot and iterative get 31/47 (66%). This is a number theory problem where the naive approach times out on large inputs. Pact's contract-driven decomposition forces the implementer to think about the math upfront. Both Pact conditions get 47/47.

3. **Base vs Research Pact**: Both achieve 100%. On this benchmark, the research changes (context fence, learnings-as-vocabulary) don't produce a measurable difference in correctness. The problems decompose into single components, so the multi-agent coordination improvements have no opportunity to demonstrate value.

4. **Cost-correctness tradeoff**: Pact costs ~23x more than single-shot but achieves 100% vs 79%. For the 45 test cases where Claude Code fails (2016_L + 2020_M), Pact's structured approach is the difference.

5. **Shaping has no significant effect**: Preliminary runs showed shape (72%) vs noshape (73%) — within noise. Not included in final comparison.

## Implementation Details

### Critical Bug Fix

The initial Pact runs scored 51-64% — worse than single-shot. Root cause: Pact's implementation prompt produced importable Python modules without `if __name__ == "__main__"` entry points. The code was logically correct but produced no output when executed as scripts.

**Fix** (2 lines added to implementer.py prompt):
```
- If the task reads from stdin/stdout, the module MUST be directly executable as a script
  (include `if __name__ == "__main__": main()`)
- Also check task.md and any test_harness.py in the project root
```

This fix was applied to both base and research Pact.

### Other Fixes Applied During Experiment

1. **Pydantic validation**: LLM sometimes returns lists/dicts for string fields. Added `model_validator` to coerce types.
2. **Diagnose phase loop**: Problems scoring 57/58 internal tests would loop in diagnose for 50 cycles. Added `phase=complete` as termination condition.
3. **Shell script line endings**: Write tool produces Windows line endings on macOS. Fixed with `sed`.

### Decomposition Pattern

All 5 problems were decomposed into exactly 1 component by Pact. This benchmark does not test multi-agent coordination — each problem is a single self-contained algorithm. A multi-component benchmark (e.g., web application with frontend + backend + database) would better test Pact's decomposition and coordination capabilities.

## Reproducibility

- Problem data: `*.json` files contain all test cases from ICPC World Finals
- Single-shot code: `run_single_shot.py`
- Iterative code: `run_iterative.py`
- Pact runner: `run_pact_problem.sh` (research), `run_pact_problem_base.sh` (base)
- Evaluation: Run implementations against test cases in JSON files
- All Pact state preserved in `pact_*/problem/.pact/` directories

## Conclusions

1. Pact's contract-first approach adds value on problems where upfront analysis matters (number theory, algorithmic optimization). The structured decomposition forces the LLM to analyze constraints before coding.

2. The cost premium (~23x) may be justified for production use cases where correctness matters more than cost.

3. This benchmark does not test Pact's multi-agent coordination or component composition, which is its primary design goal. Future benchmarks should use multi-component projects.

4. The research changes (context fence, learnings-as-vocabulary) show no effect on single-component problems. Testing on multi-component projects is needed to evaluate these changes.
