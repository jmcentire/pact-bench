#!/usr/bin/env python3
"""Run Claude iterative (with test feedback) on ICPC problems.

Usage: python run_iterative.py [problem_id ...]
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
MAX_ITERATIONS = 5


def test_code(code: str, test_cases: list[dict]) -> tuple[int, int, list[str]]:
    """Run code against test cases. Returns (passed, total, failure_details)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        code_file = f.name

    passed = 0
    total = len(test_cases)
    failures = []

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
                    exp_short = expected[:60].replace('\n', '\\n')
                    act_short = actual[:60].replace('\n', '\\n')
                    failures.append(f"tc_{i}: expected '{exp_short}', got '{act_short}'")
            except subprocess.TimeoutExpired:
                failures.append(f"tc_{i}: TIMEOUT (>30s)")
            except Exception as e:
                failures.append(f"tc_{i}: RUNTIME ERROR: {e}")
    finally:
        os.unlink(code_file)

    return passed, total, failures


def run_problem(client, problem_id: str, project_dir: Path) -> dict:
    """Run iterative Claude on one ICPC problem."""
    data = json.loads((project_dir / f"{problem_id}.json").read_text())

    prompt = f"""Solve this competitive programming problem. Write a Python 3 program that reads from stdin and writes to stdout.

## Problem

{data['question_content']}

## Instructions

Write a complete Python program. It should read input from stdin and print output to stdout.
Output ONLY the Python code, no markdown fences, no explanation."""

    messages = [{"role": "user", "content": prompt}]
    test_cases = data['test_cases']
    total_in_tokens = 0
    total_out_tokens = 0
    total_time = 0

    for iteration in range(1, MAX_ITERATIONS + 1):
        start = time.time()
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8192,
            messages=messages,
        )
        elapsed = time.time() - start
        total_time += elapsed

        code = response.content[0].text
        total_in_tokens += response.usage.input_tokens
        total_out_tokens += response.usage.output_tokens

        # Strip markdown fences
        if code.startswith("```"):
            lines = code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)

        passed, total, failures = test_code(code, test_cases)
        print(f"    Iter {iteration}: {passed}/{total} ({elapsed:.1f}s)")

        if passed == total:
            break

        if iteration < MAX_ITERATIONS:
            # Feed first 5 failures + summary back
            fail_sample = "\n".join(failures[:5])
            if len(failures) > 5:
                fail_sample += f"\n... and {len(failures)-5} more failures"

            feedback = f"""Your solution passes {passed}/{total} test cases.

Failing test cases:
{fail_sample}

Fix the implementation. Output the COMPLETE fixed program.
Output ONLY Python code, no markdown fences."""

            messages.append({"role": "assistant", "content": response.content[0].text})
            messages.append({"role": "user", "content": feedback})

    cost_in = total_in_tokens * 15.0 / 1_000_000
    cost_out = total_out_tokens * 75.0 / 1_000_000
    cost = cost_in + cost_out

    result = {
        "problem_id": problem_id,
        "title": data['question_title'],
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total else 0,
        "iterations": iteration,
        "cost_usd": round(cost, 4),
        "time_seconds": round(total_time, 1),
        "input_tokens": total_in_tokens,
        "output_tokens": total_out_tokens,
        "failures": failures[:5],
    }

    print(f"  {problem_id} ({data['question_title']}): {passed}/{total} "
          f"({result['pass_rate']*100:.0f}%) in {iteration} iters, "
          f"${cost:.4f} {total_time:.1f}s")

    return result


def main():
    project_dir = Path(__file__).parent.resolve()
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    problems = sys.argv[1:] if len(sys.argv) > 1 else PROBLEMS

    print(f"Running iterative Claude on {len(problems)} ICPC problems "
          f"(max {MAX_ITERATIONS} iterations each)\n")

    results = []
    for pid in problems:
        r = run_problem(client, pid, project_dir)
        results.append(r)

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
              f"iters={r['iterations']} ${r['cost_usd']:.4f} {r['time_seconds']:.1f}s  {r['title']}")

    run_num = 1
    while (project_dir / f"results_iterative_run{run_num}.json").exists():
        run_num += 1
    out_file = project_dir / f"results_iterative_run{run_num}.json"
    with open(out_file, 'w') as f:
        json.dump({
            "run": run_num,
            "model": "claude-opus-4-6",
            "condition": "iterative (test feedback)",
            "max_iterations": MAX_ITERATIONS,
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
