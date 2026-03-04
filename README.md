# Pact Benchmark: ICPC World Finals

Benchmark comparing [Pact](https://github.com/jmcentire/pact) against Claude Code on 5 ICPC World Finals competitive programming problems (212 test cases).

## Results

| Condition | Pass Rate | Cost |
|-----------|-----------|------|
| Claude Code (single-shot) | 167/212 (79%) | $0.60 |
| Claude Code (iterative, 5 attempts) | 196/212 (92%) | $1.26 |
| Pact base (solo, noshape) | **212/212 (100%)** | ~$13 |
| Pact research (solo, noshape) | **212/212 (100%)** | $13.71 |

### Per-Problem Breakdown

| Problem | Single-shot | Iterative | Pact Base | Pact Research |
|---------|-------------|-----------|-----------|---------------|
| 2012_D Fibonacci Words (35) | 35/35 | 35/35 | 35/35 | 35/35 |
| 2016_E Forever Young (60) | 60/60 | 60/60 | 60/60 | 60/60 |
| 2016_L Swap Space (29) | 0/29 | 29/29 | 29/29 | 29/29 |
| 2017_F Posterize (41) | 41/41 | 41/41 | 41/41 | 41/41 |
| 2020_M Trailing Digits (47) | 31/47 | 31/47 | **47/47** | **47/47** |

### Key Finding

**Trailing Digits** (2020 World Finals) is the decisive problem. Claude Code scores 31/47 even with 5 retry iterations and full test feedback -- the naive algorithm times out on large inputs. Pact's interview and decomposition phases force upfront mathematical analysis, producing the correct O(log n) approach on the first implementation attempt.

See [RESULTS.md](RESULTS.md) for the full analysis.

## Setup

All conditions use Claude Opus 4.6. Pact uses Sonnet 4 for planning phases and Claude Code (Opus 4.6) for implementation.

### Decompress test data

```bash
cd testdata
gunzip -k *.gz
```

### Reproduce baselines

```bash
# Requires ANTHROPIC_API_KEY
python scripts/run_single_shot.py
python scripts/run_iterative.py
```

### Reproduce Pact runs

```bash
# Requires pact installed: pip install pact-agents
# Setup condition directories
python scripts/setup_benchmark.py

# Run a single condition
bash scripts/run_condition.sh pact_research_noshape_solo research
bash scripts/run_condition.sh pact_base_noshape_solo base
```

### Evaluate

```bash
python scripts/evaluate_all.py
```

## Repository Structure

```
testdata/           # ICPC test cases (gzipped JSON: input/output pairs)
baselines/          # Claude Code results (single-shot and iterative)
conditions/         # Pact run state and implementations
  pact_research_noshape_solo/   # Research Pact (context fence + vocabulary)
  pact_base_noshape_solo/       # Base Pact (release version)
scripts/            # Benchmark runner scripts
results_final.json  # Machine-readable combined results
RESULTS.md          # Full analysis and methodology
```

## Problems

| ID | Problem | Source | Tests | Domain |
|----|---------|--------|-------|--------|
| 2012_D | Fibonacci Words | ICPC 2012 World Finals | 35 | String pattern counting in Fibonacci-concatenated strings |
| 2016_E | Forever Young | ICPC 2016 World Finals | 60 | Date arithmetic with digit reversal |
| 2016_L | Swap Space | ICPC 2016 World Finals | 29 | Optimal disk reformatting order |
| 2017_F | Posterize | ICPC 2017 World Finals | 41 | Dynamic programming for color quantization |
| 2020_M | Trailing Digits | ICPC 2020 World Finals | 47 | Number theory -- trailing digits in multiples |

## License

MIT
