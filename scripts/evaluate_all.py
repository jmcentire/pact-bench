#!/usr/bin/env python3
"""Evaluate all Pact condition solutions against official ICPC test cases.

Finds implementation files in .pact/implementations/ and runs them against
the test cases from the problem JSON files.

Usage: python evaluate_all.py
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROBLEMS = ['2016_L', '2016_E', '2012_D', '2017_F', '2020_M']
PROJECT_DIR = Path(__file__).parent.resolve()

PACT_CONDITIONS = [
    ('pact_base_noshape_solo', 'base'),
    ('pact_base_noshape_competitive', 'base'),
    ('pact_base_shape_solo', 'base'),
    ('pact_base_shape_competitive', 'base'),
    ('pact_research_noshape_solo', 'research'),
    ('pact_research_noshape_competitive', 'research'),
    ('pact_research_shape_solo', 'research'),
    ('pact_research_shape_competitive', 'research'),
]


def find_solution(prob_dir: Path) -> Path | None:
    """Find the best implementation file in a Pact problem directory."""
    impl_root = prob_dir / '.pact' / 'implementations'
    if not impl_root.exists():
        return None

    # Look for solution.py or any .py file
    candidates = []
    for dirpath, _, filenames in os.walk(impl_root):
        for f in filenames:
            if f.endswith('.py'):
                candidates.append(Path(dirpath) / f)

    if not candidates:
        return None

    # Prefer solution.py, then largest file
    for c in candidates:
        if c.name == 'solution.py':
            return c
    return max(candidates, key=lambda p: p.stat().st_size)


def test_solution(code_path: Path, test_cases: list[dict]) -> tuple[int, int, list[str]]:
    """Run solution against test cases. Returns (passed, total, failures)."""
    passed = 0
    total = len(test_cases)
    failures = []

    for i, tc in enumerate(test_cases):
        inp = tc['input']
        expected = tc['output'].strip()

        try:
            result = subprocess.run(
                [sys.executable, str(code_path)],
                input=inp, capture_output=True, text=True, timeout=30
            )
            actual = result.stdout.strip()

            if actual == expected:
                passed += 1
            else:
                exp_short = expected[:60].replace('\n', '\\n')
                act_short = actual[:60].replace('\n', '\\n')
                failures.append(f"tc_{i}: expected '{exp_short}', got '{act_short}'")
        except subprocess.TimeoutExpired:
            failures.append(f"tc_{i}: TIMEOUT")
        except Exception as e:
            failures.append(f"tc_{i}: ERROR: {e}")

    return passed, total, failures


def get_pact_cost(prob_dir: Path) -> float:
    """Extract cost from Pact state.json."""
    state_file = prob_dir / '.pact' / 'state.json'
    if state_file.exists():
        state = json.loads(state_file.read_text())
        return state.get('total_cost_usd', 0.0)
    return 0.0


def get_pact_status(prob_dir: Path) -> str:
    """Extract status from Pact state.json."""
    state_file = prob_dir / '.pact' / 'state.json'
    if state_file.exists():
        state = json.loads(state_file.read_text())
        return state.get('status', 'unknown')
    return 'not_started'


def main():
    all_results = {}

    for cond_name, variant in PACT_CONDITIONS:
        cond_results = []
        print(f"\n=== {cond_name} ({variant}) ===")

        for pid in PROBLEMS:
            prob_dir = PROJECT_DIR / cond_name / pid
            data = json.loads((PROJECT_DIR / f'{pid}.json').read_text())
            test_cases = data['test_cases']

            status = get_pact_status(prob_dir)
            cost = get_pact_cost(prob_dir)
            sol = find_solution(prob_dir)

            if sol is None:
                print(f"  {pid}: NO SOLUTION (status={status}, cost=${cost:.4f})")
                cond_results.append({
                    'problem_id': pid,
                    'title': data['question_title'],
                    'passed': 0,
                    'total': len(test_cases),
                    'pass_rate': 0.0,
                    'cost_usd': round(cost, 4),
                    'status': status,
                    'solution_found': False,
                })
                continue

            passed, total, failures = test_solution(sol, test_cases)
            rate = passed / total if total else 0

            print(f"  {pid} ({data['question_title']}): {passed}/{total} "
                  f"({rate*100:.0f}%) ${cost:.4f} status={status}")
            if failures:
                for f in failures[:3]:
                    print(f"    FAIL: {f}")
                if len(failures) > 3:
                    print(f"    ... and {len(failures)-3} more")

            cond_results.append({
                'problem_id': pid,
                'title': data['question_title'],
                'passed': passed,
                'total': total,
                'pass_rate': round(rate, 3),
                'cost_usd': round(cost, 4),
                'status': status,
                'solution_found': True,
                'solution_path': str(sol.relative_to(PROJECT_DIR)),
                'failures': failures[:5],
            })

        total_passed = sum(r['passed'] for r in cond_results)
        total_tests = sum(r['total'] for r in cond_results)
        total_cost = sum(r['cost_usd'] for r in cond_results)
        rate = total_passed / total_tests if total_tests else 0

        print(f"  TOTAL: {total_passed}/{total_tests} ({rate*100:.0f}%) ${total_cost:.4f}")

        all_results[cond_name] = {
            'variant': variant,
            'total_passed': total_passed,
            'total_tests': total_tests,
            'overall_pass_rate': round(rate, 3),
            'total_cost_usd': round(total_cost, 4),
            'problems': cond_results,
        }

    # Load baseline results if available
    for pattern, label in [('results_run*.json', 'single_shot'), ('results_iterative_run*.json', 'iterative')]:
        import glob
        files = sorted(glob.glob(str(PROJECT_DIR / pattern)))
        if files:
            latest = files[-1]
            data = json.loads(Path(latest).read_text())
            all_results[label] = data

    # Save combined results
    out_file = PROJECT_DIR / 'results_all.json'
    with open(out_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved combined results to {out_file}")

    # Print comparison table
    print(f"\n{'='*80}")
    print(f"{'Condition':<40s} {'Passed':>8s} {'Total':>6s} {'Rate':>6s} {'Cost':>8s}")
    print(f"{'='*80}")
    for name, data in all_results.items():
        if isinstance(data, dict) and 'total_passed' in data:
            tp = data['total_passed']
            tt = data['total_tests']
            rate = data.get('overall_pass_rate', tp/tt if tt else 0)
            cost = data.get('total_cost_usd', 0)
            print(f"{name:<40s} {tp:>8d} {tt:>6d} {rate*100:>5.1f}% ${cost:>7.4f}")


if __name__ == '__main__':
    main()
