"""Posterize solver: minimum SSE via contiguous group partitioning DP."""

from __future__ import annotations

import sys
from typing import NamedTuple


class RedPixelPair(NamedTuple):
    """A single distinct red value and its associated pixel count."""
    r: int
    p: int


class ParsedInput(NamedTuple):
    """Fully parsed input for one test case."""
    d: int
    k: int
    values: list[RedPixelPair]


class PrefixSums(NamedTuple):
    """Three prefix sum arrays enabling O(1) cost computation."""
    s0: list[int]
    s1: list[int]
    s2: list[int]


RedPixelPairList = list[RedPixelPair]
IntList = list[int]


def parse_input() -> ParsedInput:
    """Read and parse a single test case from stdin."""
    data = sys.stdin.read().split()
    if not data:
        raise ValueError("No input available on stdin.")
    try:
        tokens = [int(t) for t in data]
    except ValueError:
        raise ValueError("Malformed input: cannot parse expected integer tokens.")

    if len(tokens) < 2:
        raise ValueError("Malformed input: cannot parse expected integer tokens.")

    d = tokens[0]
    k = tokens[1]

    if d < 1 or d > 256:
        raise ValueError("Input values violate problem constraints.")
    if k < 1 or k > d:
        raise ValueError("Input values violate problem constraints.")
    if len(tokens) != 2 + 2 * d:
        raise ValueError("Malformed input: cannot parse expected integer tokens.")

    values: list[RedPixelPair] = []
    for i in range(d):
        r = tokens[2 + 2 * i]
        p = tokens[2 + 2 * i + 1]
        if r < 0 or r > 255:
            raise ValueError("Input values violate problem constraints.")
        if p < 1:
            raise ValueError("Input values violate problem constraints.")
        values.append(RedPixelPair(r, p))

    values.sort(key=lambda v: v.r)
    return ParsedInput(d, k, values)


def build_prefix_sums(values: RedPixelPairList) -> PrefixSums:
    """Compute prefix sum arrays s0, s1, s2 from sorted (r, p) pairs."""
    if not values:
        raise ValueError("Cannot build prefix sums from an empty values list.")

    d = len(values)
    s0 = [0] * (d + 1)
    s1 = [0] * (d + 1)
    s2 = [0] * (d + 1)
    for i in range(d):
        r = values[i][0]
        p = values[i][1]
        s0[i + 1] = s0[i] + p
        s1[i + 1] = s1[i] + p * r
        s2[i + 1] = s2[i] + p * r * r
    return PrefixSums(s0, s1, s2)


def cost(i: int, j: int, s0: IntList, s1: IntList, s2: IntList) -> int:
    """Minimum weighted SSE for group i..j with a single integer representative in [0,255]."""
    if i < 0 or j < i or j + 1 >= len(s0):
        raise IndexError("Index range (i, j) is out of bounds for the prefix sum arrays.")

    sum_p = s0[j + 1] - s0[i]
    sum_pr = s1[j + 1] - s1[i]
    sum_pr2 = s2[j + 1] - s2[i]

    if sum_p == 0:
        raise ValueError("Group has zero total pixel count; weighted mean is undefined.")

    # Weighted mean; try floor and ceil
    v_floor = sum_pr // sum_p
    v_ceil = v_floor + (1 if sum_pr % sum_p != 0 else 0)

    # Clamp to [0, 255]
    v_floor = max(0, min(255, v_floor))
    v_ceil = max(0, min(255, v_ceil))

    def sse(v: int) -> int:
        return sum_pr2 - 2 * v * sum_pr + v * v * sum_p

    return min(sse(v_floor), sse(v_ceil))


def solve(d: int, k: int, s0: IntList, s1: IntList, s2: IntList) -> int:
    """Minimum total SSE via contiguous group partitioning DP."""
    if d < 1 or d > 256:
        raise ValueError("d is out of allowed range [1, 256].")
    if k < 1 or k > 256:
        raise ValueError("k is out of allowed range [1, 256].")
    if len(s0) != d + 1 or len(s1) != d + 1 or len(s2) != d + 1:
        raise ValueError("Prefix sum arrays must each have length d + 1.")

    if k >= d:
        return 0

    # dp[i] = min SSE for first i values using g groups (rolling over g)
    INF = float('inf')

    # Base case: g=1
    prev = [INF] * (d + 1)
    prev[0] = 0
    for i in range(1, d + 1):
        prev[i] = cost(0, i - 1, s0, s1, s2)

    for g in range(2, k + 1):
        curr = [INF] * (d + 1)
        curr[0] = 0
        for i in range(g, d + 1):
            best = INF
            for m in range(g - 1, i):
                c = prev[m] + cost(m, i - 1, s0, s1, s2)
                if c < best:
                    best = c
            curr[i] = best
        prev = curr

    return int(prev[d])


def main() -> None:
    """Entry point: parse, build prefix sums, solve, print result."""
    parsed = parse_input()
    ps = build_prefix_sums(parsed.values)
    result = solve(parsed.d, parsed.k, ps.s0, ps.s1, ps.s2)
    print(result)


if __name__ == "__main__":
    main()
