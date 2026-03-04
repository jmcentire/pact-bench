"""Swap Space solution: compute minimum extra storage to reformat all drives."""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class Drive:
    """A single drive with its old (pre-reformat) capacity and new (post-reformat) capacity."""
    old_capacity: int
    new_capacity: int


DriveList = list[Drive]


@dataclass
class RawInput:
    """Parsed representation of the full problem input from stdin."""
    n: int
    drives: DriveList


def parse_input(raw_text: str) -> RawInput:
    """Parse raw input text into a RawInput structure."""
    if not raw_text or raw_text.isspace():
        raise ValueError("Input is empty.")

    tokens = raw_text.split()
    if len(tokens) == 0:
        raise ValueError("Input is empty.")

    try:
        n = int(tokens[0])
    except ValueError:
        raise ValueError("Input contains a non-integer token.")

    if n < 1 or n > 10**6:
        raise ValueError("n is out of valid range [1, 10^6].")

    expected = 1 + 2 * n
    if len(tokens) < expected:
        raise ValueError("Input does not contain the expected number of tokens.")

    drives: DriveList = []
    idx = 1
    for _ in range(n):
        try:
            a = int(tokens[idx])
            b = int(tokens[idx + 1])
        except ValueError:
            raise ValueError("Input contains a non-integer token.")
        if a < 1 or a > 10**9 or b < 1 or b > 10**9:
            raise ValueError("Drive capacity is out of valid range [1, 10^9].")
        drives.append(Drive(old_capacity=a, new_capacity=b))
        idx += 2

    return RawInput(n=n, drives=drives)


def solve(drives: DriveList) -> int:
    """Compute the minimum extra storage E needed to reformat all drives."""
    if len(drives) == 0:
        raise ValueError("Drive list must be non-empty.")

    growers: list[Drive] = []
    shrinkers: list[Drive] = []

    for d in drives:
        if d.new_capacity >= d.old_capacity:
            growers.append(d)
        else:
            shrinkers.append(d)

    growers.sort(key=lambda d: d.old_capacity)
    shrinkers.sort(key=lambda d: d.new_capacity, reverse=True)

    ordered = growers + shrinkers

    free = 0
    min_free = 0
    for d in ordered:
        free -= d.old_capacity
        if free < min_free:
            min_free = free
        free += d.new_capacity

    return max(0, -min_free)


def main() -> None:
    """Entry point. Reads stdin, solves, prints result."""
    raw_text = sys.stdin.read()
    parsed = parse_input(raw_text)
    result = solve(parsed.drives)
    print(result)


if __name__ == "__main__":
    main()
