"""Fibonacci Words — count overlapping occurrences of a pattern in F(n)."""
import sys
from typing import List, NamedTuple

FailureTable = List[int]
FibStateList = list  # list of FibState


class FibState(NamedTuple):
    count: int
    prefix: str
    suffix: str


class InputPair(NamedTuple):
    n: int
    pattern: str


InputPairList = List[InputPair]


def build_failure(pattern: str) -> FailureTable:
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty.")
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


def count_overlapping(text: str, pattern: str, failure: FailureTable) -> int:
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty.")
    if len(failure) != len(pattern):
        raise ValueError("Failure table length must match pattern length.")
    m = len(pattern)
    count = 0
    k = 0
    for ch in text:
        while k > 0 and pattern[k] != ch:
            k = failure[k - 1]
        if pattern[k] == ch:
            k += 1
        if k == m:
            count += 1
            k = failure[k - 1]
    return count


def solve(n: int, pattern: str) -> int:
    if n < 0 or n > 100:
        raise ValueError("n must be between 0 and 100 inclusive.")
    if len(pattern) == 0:
        raise ValueError("Pattern must be non-empty.")
    if not all(c in '01' for c in pattern):
        raise ValueError("Pattern must consist only of '0' and '1'.")

    m = len(pattern)
    failure = build_failure(pattern)
    boundary = m - 1  # length of prefix/suffix we need to track

    # For pattern of length 1, boundary = 0, so prefix/suffix are empty strings
    # and we only need to count directly in base cases and sum.

    # Cap for fib_len to avoid huge integers
    cap = m + 1

    # Base cases
    base_words = ["0", "1"]
    states: list = [None, None]
    fib_len = [0] * (max(n, 1) + 1)

    for i in range(2):
        w = base_words[i]
        fib_len[i] = 1
        c = count_overlapping(w, pattern, failure)
        p = w[:boundary] if boundary > 0 else ""
        s = w[-boundary:] if boundary > 0 else ""
        states[i] = FibState(count=c, prefix=p, suffix=s)

    if n <= 1:
        return states[n].count

    for k in range(2, n + 1):
        fib_len[k] = fib_len[k - 1] + fib_len[k - 2]
        if fib_len[k] > cap:
            fib_len[k] = cap

        prev = states[1]  # F(k-1)
        prev2 = states[0]  # F(k-2)

        # Cross-boundary matches
        junction = prev.suffix + prev2.prefix
        cross = count_overlapping(junction, pattern, failure)
        # Subtract matches that are entirely within suffix or prefix
        cross -= count_overlapping(prev.suffix, pattern, failure)
        cross -= count_overlapping(prev2.prefix, pattern, failure)

        total = prev.count + prev2.count + cross

        # New prefix and suffix
        blen = min(fib_len[k], boundary)
        if boundary == 0:
            new_prefix = ""
            new_suffix = ""
        else:
            # prefix of F(k) = F(k-1) + F(k-2)
            # Take first blen chars: starts with prefix of F(k-1)
            combined_prefix = prev.prefix + prev2.prefix
            new_prefix = combined_prefix[:blen]

            # suffix of F(k): ends with suffix of F(k-2)
            combined_suffix = prev.suffix + prev2.suffix
            new_suffix = combined_suffix[-blen:] if blen > 0 else ""

        states[0] = states[1]
        states[1] = FibState(count=total, prefix=new_prefix, suffix=new_suffix)

    return states[1].count


def main() -> None:
    data = sys.stdin.read()
    lines = [line for line in data.split('\n') if line.strip()]

    if len(lines) % 2 != 0:
        raise ValueError("Input contains an incomplete test case (odd number of non-empty lines).")

    case_num = 0
    for i in range(0, len(lines), 2):
        try:
            n = int(lines[i])
        except ValueError:
            raise ValueError("Expected a non-negative integer for n.")
        if n < 0:
            raise ValueError("Expected a non-negative integer for n.")
        pattern = lines[i + 1].strip()
        case_num += 1
        result = solve(n, pattern)
        sys.stdout.write(f"Case {case_num}: {result}\n")


if __name__ == "__main__":
    main()
