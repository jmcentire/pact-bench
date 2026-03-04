import sys
from typing import NamedTuple

Drive = NamedTuple("Drive", [("a", int), ("b", int)])
DriveList = list[Drive]
ExtraSpace = int


def parse_input() -> DriveList:
    tokens = sys.stdin.read().split()
    if not tokens:
        raise ValueError("No input available on stdin.")
    n = int(tokens[0])
    if n < 0:
        raise ValueError("First token is not a valid non-negative integer for n.")
    if len(tokens) < 1 + 2 * n:
        raise ValueError("Input contains fewer drive entries than specified by n.")
    drives: DriveList = []
    for i in range(n):
        a = int(tokens[1 + 2 * i])
        b = int(tokens[2 + 2 * i])
        drives.append((a, b))
    return drives


def solve(drives: DriveList) -> ExtraSpace:
    for a, b in drives:
        if a < 0 or b < 0:
            raise ValueError("Drive capacities must be non-negative.")

    gainers = [(a, b) for a, b in drives if b >= a]
    losers = [(a, b) for a, b in drives if b < a]
    gainers.sort(key=lambda d: d[0])
    losers.sort(key=lambda d: d[1], reverse=True)

    ordered = gainers + losers
    needed = 0
    prefix_net = 0
    for a, b in ordered:
        # Before processing this drive, free_space = S + prefix_net
        # Need S + prefix_net >= a, i.e. S >= a - prefix_net
        needed = max(needed, a - prefix_net)
        prefix_net += b - a
    return max(0, needed)


def main() -> None:
    drives = parse_input()
    print(solve(drives))


if __name__ == "__main__":
    main()
