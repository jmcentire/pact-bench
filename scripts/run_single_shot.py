#!/usr/bin/env python3
"""Run Claude single-shot on ICPC problems.

Usage: python run_single_shot.py [problem_id ...]
       python run_single_shot.py              # runs all 5
       python run_single_shot.py 2015_A       # runs one
"""

import json
import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

import anthropic


PROBLEMS = ['2016_L', '2016_E', '2012_D', '2017_F', '2020_M']


def run_problem(client, problem_id: str, project_dir: Path) -> dict:
    """Run single-shot Claude on one ICPC problem."""
    data = json.loads((project_dir / f"{problem_id}.json").read_text())

    prompt = f"""Solve this competitive programming problem. Write a Python 3 program that reads from stdin and writes to stdout.

## Problem

{data['question_content']}

## Instructions

Write a complete Python program. It should read input from stdin and print output to stdout.
Output ONLY the Python code, no markdown fences, no explanation."""

    start = time.time()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - start

    code = response.content[0].text
    if code.startswith("```"):
        lines = code.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)

    # Test against all test cases
    test_cases = data['test_cases']
    passed = 0
    total = len(test_cases)
    failures = []

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        code_file = f.name

    try:
        for i, tc in enumerate(test_cases):
            inp = tc['input']
            expected = tc['output'].strip()

            try:
                result = subprocess.run(
                    [sys.executable, code_file],
                    input=inp, capture_output=True, text=True, timeout=30
                )
                actual = result.stdout.strip()

                if actual == expected:
                    passed += 1
                else:
                    # Show first difference for debugging
                    exp_lines = expected.split('\n')
                    act_lines = actual.split('\n')
                    diff_line = ""
                    for j, (e, a) in enumerate(zip(exp_lines, act_lines)):
                        if e != a:
                            diff_line = f" (line {j+1}: expected '{e[:50]}', got '{a[:50]}')"
                            break
                    if len(exp_lines) != len(act_lines):
                        diff_line += f" (expected {len(exp_lines)} lines, got {len(act_lines)})"
                    failures.append(f"tc_{i}{diff_line}")
            except subprocess.TimeoutExpired:
                failures.append(f"tc_{i}: TIMEOUT")
            except Exception as e:
                failures.append(f"tc_{i}: ERROR {e}")
    finally:
        os.unlink(code_file)

    cost_in = response.usage.input_tokens * 15.0 / 1_000_000
    cost_out = response.usage.output_tokens * 75.0 / 1_000_000
    cost = cost_in + cost_out

    result = {
        "problem_id": problem_id,
        "title": data['question_title'],
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total else 0,
        "cost_usd": round(cost, 4),
        "time_seconds": round(elapsed, 1),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "failures": failures[:10],  # first 10 failures only
    }

    print(f"  {problem_id} ({data['question_title']}): {passed}/{total} "
          f"({result['pass_rate']*100:.0f}%) ${cost:.4f} {elapsed:.1f}s")
    if failures:
        for f in failures[:3]:
            print(f"    FAIL: {f}")
        if len(failures) > 3:
            print(f"    ... and {len(failures)-3} more failures")

    return result


def main():
    project_dir = Path(__file__).parent.resolve()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    problems = sys.argv[1:] if len(sys.argv) > 1 else PROBLEMS

    print(f"Running single-shot Claude on {len(problems)} ICPC problems\n")

    results = []
    for pid in problems:
        r = run_problem(client, pid, project_dir)
        results.append(r)

    # Summary
    total_passed = sum(r['passed'] for r in results)
    total_tests = sum(r['total'] for r in results)
    total_cost = sum(r['cost_usd'] for r in results)
    total_time = sum(r['time_seconds'] for r in results)

    print(f"\n{'='*60}")
    print(f"Overall: {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)")
    print(f"Cost: ${total_cost:.4f}  Time: {total_time:.1f}s")
    print()
    for r in results:
        print(f"  {r['problem_id']:10s} {r['passed']:3d}/{r['total']:3d} ({r['pass_rate']*100:5.1f}%) "
              f"${r['cost_usd']:.4f} {r['time_seconds']:.1f}s  {r['title']}")

    # Save
    run_num = 1
    while (project_dir / f"results_run{run_num}.json").exists():
        run_num += 1
    out_file = project_dir / f"results_run{run_num}.json"
    with open(out_file, 'w') as f:
        json.dump({
            "run": run_num,
            "model": "claude-opus-4-6",
            "condition": "single-shot",
            "total_passed": total_passed,
            "total_tests": total_tests,
            "overall_pass_rate": round(total_passed / total_tests, 3),
            "total_cost_usd": round(total_cost, 4),
            "total_time_seconds": round(total_time, 1),
            "problems": results,
        }, f, indent=2)
    print(f"\nSaved to {out_file}")


if __name__ == "__main__":
    main()
