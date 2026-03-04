#!/usr/bin/env python3
"""Set up the official ICPC Pact benchmark — 10 conditions.

Conditions:
  1. single_shot         — Claude Opus 4.6, one attempt
  2. iterative           — Claude Opus 4.6, up to 5 iterations with test feedback
  3. pact_base_noshape_solo        — Base Pact, no shaping, solo implementation
  4. pact_base_noshape_competitive — Base Pact, no shaping, competitive implementations
  5. pact_base_shape_solo          — Base Pact, shaping, solo implementation
  6. pact_base_shape_competitive   — Base Pact, shaping, competitive implementations
  7. pact_research_noshape_solo        — Research Pact, no shaping, solo
  8. pact_research_noshape_competitive — Research Pact, no shaping, competitive
  9. pact_research_shape_solo          — Research Pact, shaping, solo
  10. pact_research_shape_competitive  — Research Pact, shaping, competitive

Each Pact condition gets a directory per problem with task.md, sops.md, pact.yaml,
and test_harness.py.
"""

import json
import os
import shutil
from pathlib import Path

PROBLEMS = ['2016_L', '2016_E', '2012_D', '2017_F', '2020_M']
SOURCE_DIR = Path(__file__).parent.parent / 'icpc'  # original problem data
DEST_DIR = Path(__file__).parent

PACT_CONDITIONS = [
    # (dir_name, variant, shaping, competitive)
    ('pact_base_noshape_solo',        'base',     False, False),
    ('pact_base_noshape_competitive', 'base',     False, True),
    ('pact_base_shape_solo',          'base',     True,  False),
    ('pact_base_shape_competitive',   'base',     True,  True),
    ('pact_research_noshape_solo',        'research', False, False),
    ('pact_research_noshape_competitive', 'research', False, True),
    ('pact_research_shape_solo',          'research', True,  False),
    ('pact_research_shape_competitive',   'research', True,  True),
]

SOPS = """# Coding Standards

- Python 3.10+ with type annotations.
- Standard library only.
- Program reads from stdin, writes to stdout.
- Must handle all input constraints from the problem statement.
- Output must match expected format exactly (including whitespace and newlines).
"""


def make_task_md(problem_data: dict, has_tests: bool) -> str:
    """Generate task.md from problem JSON."""
    content = f"# {problem_data['question_title']}\n\n"
    content += f"# Problem Description\n\n{problem_data['question_content']}\n"

    if has_tests:
        content += "\n## Test Cases\n\n"
        content += "A test harness with official test cases is provided in test_harness.py.\n"
        content += "Run: `python test_harness.py solution.py`\n"

    return content


def make_test_harness(problem_data: dict) -> str:
    """Generate test_harness.py from problem JSON."""
    tests = problem_data['test_cases']
    lines = [
        '#!/usr/bin/env python3',
        '"""Test harness with official ICPC test cases."""',
        'import subprocess, sys, os',
        '',
        'TESTS = [',
    ]
    for tc in tests:
        inp = repr(tc['input'])
        out = repr(tc['output'].strip())
        lines.append(f'    ({inp}, {out}),')
    lines.append(']')
    lines.append('')
    lines.append('def main():')
    lines.append('    if len(sys.argv) < 2:')
    lines.append('        print("Usage: python test_harness.py <solution.py>")')
    lines.append('        sys.exit(1)')
    lines.append('    sol = sys.argv[1]')
    lines.append('    passed = 0')
    lines.append('    for i, (inp, expected) in enumerate(TESTS):')
    lines.append('        try:')
    lines.append('            r = subprocess.run(')
    lines.append('                [sys.executable, sol], input=inp,')
    lines.append('                capture_output=True, text=True, timeout=30')
    lines.append('            )')
    lines.append('            actual = r.stdout.strip()')
    lines.append('            if actual == expected:')
    lines.append('                passed += 1')
    lines.append('            else:')
    lines.append("                print(f'FAIL tc_{i}: expected {expected[:60]!r}, got {actual[:60]!r}')")
    lines.append('        except subprocess.TimeoutExpired:')
    lines.append("            print(f'FAIL tc_{i}: TIMEOUT')")
    lines.append('        except Exception as e:')
    lines.append("            print(f'FAIL tc_{i}: {e}')")
    lines.append("    print(f'{passed}/{len(TESTS)} passed')")
    lines.append('    sys.exit(0 if passed == len(TESTS) else 1)')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    main()')
    return '\n'.join(lines) + '\n'


def make_pact_yaml(shaping: bool, competitive: bool) -> str:
    """Generate pact.yaml for a condition."""
    return f"""budget: 25.0
parallel_components: false
competitive_implementations: {'true' if competitive else 'false'}
competitive_agents: 2
max_implementation_attempts: 5
language: python
model: claude-sonnet-4-20250514
shaping: {'true' if shaping else 'false'}
health_thresholds:
  output_planning_ratio_critical: 0.0
"""


def main():
    # Copy problem data files
    for pid in PROBLEMS:
        src = SOURCE_DIR / f'{pid}.json'
        dst = DEST_DIR / f'{pid}.json'
        if src.exists():
            shutil.copy2(src, dst)
            print(f'Copied {pid}.json')
        else:
            print(f'WARNING: {src} not found')

    # Create Pact condition directories
    for cond_name, variant, shaping, competitive in PACT_CONDITIONS:
        for pid in PROBLEMS:
            prob_dir = DEST_DIR / cond_name / pid
            prob_dir.mkdir(parents=True, exist_ok=True)

            # Load problem data
            data = json.loads((SOURCE_DIR / f'{pid}.json').read_text())

            # task.md — always includes test harness reference
            (prob_dir / 'task.md').write_text(make_task_md(data, has_tests=True))

            # sops.md
            (prob_dir / 'sops.md').write_text(SOPS)

            # pact.yaml
            (prob_dir / 'pact.yaml').write_text(make_pact_yaml(shaping, competitive))

            # test_harness.py
            (prob_dir / 'test_harness.py').write_text(make_test_harness(data))

        print(f'Created {cond_name}/ (shaping={shaping}, competitive={competitive}, variant={variant})')

    # Copy baseline scripts
    for script in ['run_single_shot.py', 'run_iterative.py']:
        src = SOURCE_DIR / script
        if src.exists():
            shutil.copy2(src, DEST_DIR / script)
            print(f'Copied {script}')

    print(f'\nSetup complete. {len(PACT_CONDITIONS)} Pact conditions x {len(PROBLEMS)} problems = {len(PACT_CONDITIONS) * len(PROBLEMS)} directories.')


if __name__ == '__main__':
    main()
