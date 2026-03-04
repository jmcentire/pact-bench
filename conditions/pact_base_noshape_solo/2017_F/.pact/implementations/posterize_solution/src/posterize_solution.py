"""Posterize solution: minimize SSE when replacing red intensities with at most k allowed values."""

import sys
from typing import List, Union

IntList = List[int]
DPCell = Union[int, float]
DPRow = List[DPCell]
DPTable = List[DPRow]


class PrefixSums:
    """Three prefix sum arrays enabling O(1) interval queries."""

    def __init__(self, prefix_p: IntList, prefix_rp: IntList, prefix_r2p: IntList):
        self.prefix_p = prefix_p
        self.prefix_rp = prefix_rp
        self.prefix_r2p = prefix_r2p


class ParsedInput:
    """Fully parsed input for the Posterize problem."""

    def __init__(self, d: int, k: int, values: IntList, counts: IntList):
        self.d = d
        self.k = k
        self.values = values
        self.counts = counts


def build_prefix_sums(d: int, values: IntList, counts: IntList) -> PrefixSums:
    """Construct three prefix sum arrays from sorted values and counts."""
    prefix_p = [0] * (d + 1)
    prefix_rp = [0] * (d + 1)
    prefix_r2p = [0] * (d + 1)
    for i in range(1, d + 1):
        prefix_p[i] = prefix_p[i - 1] + counts[i - 1]
        prefix_rp[i] = prefix_rp[i - 1] + values[i - 1] * counts[i - 1]
        prefix_r2p[i] = prefix_r2p[i - 1] + values[i - 1] * values[i - 1] * counts[i - 1]
    return PrefixSums(prefix_p, prefix_rp, prefix_r2p)


def compute_cost(
    a: int,
    b: int,
    prefix_p: IntList,
    prefix_rp: IntList,
    prefix_r2p: IntList,
) -> int:
    """Compute minimum SSE for interval [a, b] with a single optimal integer representative."""
    d = len(prefix_p) - 1
    if a > b:
        raise IndexError("Interval indices out of bounds or inverted")
    if b >= d:
        raise IndexError("Interval indices out of bounds or inverted")

    sum_p = prefix_p[b + 1] - prefix_p[a]
    sum_rp = prefix_rp[b + 1] - prefix_rp[a]
    sum_r2p = prefix_r2p[b + 1] - prefix_r2p[a]

    if sum_p == 0:
        raise ZeroDivisionError("Total pixel count in interval is zero, cannot compute weighted mean")

    # Optimal integer representative: try floor and ceil of weighted mean
    # mean = sum_rp / sum_p
    v_floor = sum_rp // sum_p
    # Clamp to [0, 255]
    v_floor = max(0, min(255, v_floor))
    v_ceil = max(0, min(255, v_floor + 1))

    def sse(v: int) -> int:
        return sum_r2p - 2 * v * sum_rp + v * v * sum_p

    cost_floor = sse(v_floor)
    cost_ceil = sse(v_ceil)
    return min(cost_floor, cost_ceil)


def solve(
    d: int,
    k: int,
    values: IntList,
    counts: IntList,
) -> int:
    """Compute minimum SSE using at most k allowed values for d distinct red values."""
    if d > 0 and (len(values) == 0 or len(counts) == 0):
        raise ValueError("values and counts must each have length d")
    if len(values) != d or len(counts) != d:
        raise ValueError("Length of values and counts must match d")

    if k >= d:
        return 0

    ps = build_prefix_sums(d, values, counts)

    INF = float('inf')
    # dp[m][i] = min SSE using m allowed values for first i distinct red values
    # Use two rows to save memory
    prev = [INF] * (d + 1)
    prev[0] = 0
    # Base case m=1
    for i in range(1, d + 1):
        prev[i] = compute_cost(0, i - 1, ps.prefix_p, ps.prefix_rp, ps.prefix_r2p)

    for m in range(2, k + 1):
        curr = [INF] * (d + 1)
        curr[0] = 0
        for i in range(1, d + 1):
            for j in range(m - 1, i):
                # prev[j] = best SSE using m-1 groups for first j values; current group covers [j, i-1]
                cost = compute_cost(j, i - 1, ps.prefix_p, ps.prefix_rp, ps.prefix_r2p)
                candidate = prev[j] + cost
                if candidate < curr[i]:
                    curr[i] = candidate
        prev = curr

    result = prev[d]
    if isinstance(result, float):
        return int(result)
    return result


def main() -> None:
    """Entry point. Read input, solve, print result."""
    data = sys.stdin.read().split()
    if not data:
        raise IndexError("Insufficient tokens when parsing input")
    idx = 0
    d = int(data[idx]); idx += 1
    k = int(data[idx]); idx += 1
    values = []
    counts = []
    for _ in range(d):
        r = int(data[idx]); idx += 1
        p = int(data[idx]); idx += 1
        values.append(r)
        counts.append(p)
    print(solve(d, k, values, counts))


if __name__ == "__main__":
    main()
