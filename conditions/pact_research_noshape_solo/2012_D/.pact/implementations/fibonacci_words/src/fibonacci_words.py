"""Fibonacci Words Pattern Counter.

Counts overlapping occurrences of a bit pattern p in the Fibonacci word F(n),
where F(0)='0', F(1)='1', and F(k)=F(k-1)+F(k-2) for k>=2.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import List

KMPFailureTable = list[int]


@dataclass
class FibState:
    """Immutable per-level DP record for a single Fibonacci word F(k)."""
    count: int
    prefix: str
    suffix: str
    length: int


@dataclass
class TestCase:
    """A single parsed test case."""
    n: int
    pattern: str


def build_kmp_failure_table(pattern: str) -> KMPFailureTable:
    """Build the KMP failure (partial match) table for the given pattern."""
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty for KMP failure table construction.")
    m = len(pattern)
    failure = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = failure[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        failure[i] = k
    return failure


def count_overlapping(text: str, pattern: str) -> int:
    """Count overlapping occurrences of pattern in text using KMP."""
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty.")
    if len(text) < len(pattern):
        return 0
    failure = build_kmp_failure_table(pattern)
    count = 0
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = failure[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == len(pattern):
            count += 1
            j = failure[j - 1]
    return count


def make_base_fib_state(base_string: str, pattern: str) -> FibState:
    """Construct FibState for a base-case Fibonacci word (F(0)='0' or F(1)='1')."""
    c = count_overlapping(base_string, pattern)
    max_ps = len(pattern) - 1
    prefix = base_string[:max_ps]
    suffix = base_string[-max_ps:] if max_ps > 0 else ""
    return FibState(count=c, prefix=prefix, suffix=suffix, length=1)


def combine_fib_states(left: FibState, right: FibState, pattern: str) -> FibState:
    """Combine F(k-1) (left) and F(k-2) (right) to produce FibState for F(k)."""
    plen = len(pattern)
    max_ps = plen - 1

    # Compute cross-boundary matches
    junction = left.suffix + right.prefix
    cross = (count_overlapping(junction, pattern)
             - count_overlapping(left.suffix, pattern)
             - count_overlapping(right.prefix, pattern))

    new_count = left.count + right.count + cross

    # Compute new length (capped at plen)
    new_length = left.length + right.length
    if new_length > plen:
        new_length = plen

    # Compute prefix and suffix
    if left.length + right.length < plen:
        # The full string is left.prefix + right.prefix (since both are full strings when small)
        full = left.prefix + left.suffix if left.length <= max_ps else left.prefix
        # Actually when length < plen, prefix == suffix == full string (up to max_ps chars)
        # But if the combined length is still < plen, we can reconstruct the full string
        # left full string = left.prefix (if left.length <= max_ps, prefix IS the full string)
        # right full string = right.prefix
        # Wait - need to be more careful. When length < plen:
        #   prefix = suffix = full string (since full string length < max_ps = plen-1)
        # So full_left = left.prefix, full_right = right.prefix
        # But actually prefix and suffix are the same when length <= max_ps
        full_string = left.prefix + right.prefix  # both are full strings when small
        new_prefix = full_string[:max_ps]
        new_suffix = full_string[-max_ps:] if max_ps > 0 else ""
    else:
        # Left is long enough or combined is long enough
        # prefix: first max_ps chars of F(k) = first max_ps chars of left
        if left.length >= max_ps:
            new_prefix = left.prefix[:max_ps]
        else:
            # Need chars from left + right
            new_prefix = (left.prefix + right.prefix)[:max_ps]

        # suffix: last max_ps chars of F(k) = last max_ps chars of right... wait
        # F(k) = left + right, so last chars come from right
        if right.length >= max_ps:
            new_suffix = right.suffix[-max_ps:] if max_ps > 0 else ""
        else:
            # Need chars from left + right
            new_suffix = (left.suffix + right.suffix)[-max_ps:] if max_ps > 0 else ""

    return FibState(count=new_count, prefix=new_prefix, suffix=new_suffix, length=new_length)


def solve(n: int, pattern: str) -> int:
    """Core DP solver for counting overlapping occurrences of pattern in F(n)."""
    if n < 0 or n > 100:
        raise ValueError("n must be between 0 and 100 inclusive.")
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty.")
    if not all(c in '01' for c in pattern):
        raise ValueError("Pattern must consist only of '0' and '1'.")

    f0 = make_base_fib_state("0", pattern)
    if n == 0:
        return f0.count
    f1 = make_base_fib_state("1", pattern)
    if n == 1:
        return f1.count

    prev2, prev1 = f0, f1
    for k in range(2, n + 1):
        combined = combine_fib_states(prev1, prev2, pattern)
        prev2, prev1 = prev1, combined

    return prev1.count


def parse_input(raw_input: str) -> list[TestCase]:
    """Parse raw input string into list of TestCase values."""
    lines = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]
    if len(lines) % 2 != 0:
        raise ValueError("Input must contain an even number of non-empty lines (pairs of n and pattern).")

    cases = []
    for i in range(0, len(lines), 2):
        try:
            n = int(lines[i])
        except ValueError:
            raise ValueError("Invalid value for n: must be an integer in [0, 100].")
        if n < 0 or n > 100:
            raise ValueError("Invalid value for n: must be an integer in [0, 100].")
        pat = lines[i + 1]
        if not pat or not all(c in '01' for c in pat):
            raise ValueError("Invalid pattern: must be a non-empty string of '0' and '1'.")
        cases.append(TestCase(n=n, pattern=pat))
    return cases


def format_output(case_number: int, count: int) -> str:
    """Format a single test case result."""
    return f"Case {case_number}: {count}"


def main() -> None:
    """Entry point. Reads stdin, solves each test case, prints results."""
    raw = sys.stdin.read()
    cases = parse_input(raw)
    for i, tc in enumerate(cases, 1):
        result = solve(tc.n, tc.pattern)
        print(format_output(i, result))


if __name__ == "__main__":
    main()
