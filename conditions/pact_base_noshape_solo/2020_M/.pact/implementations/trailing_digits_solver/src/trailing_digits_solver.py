"""Trailing Digits Solver — ICPC 2020 Problem M."""

import sys
sys.set_int_max_str_digits(0)

from dataclasses import dataclass
from enum import Enum
from math import gcd


@dataclass
class ProblemInput:
    """Parsed input for the Trailing Digits problem."""
    b: int
    d: int
    a: int


class CongruenceResult(Enum):
    """Outcome of attempting to solve the modular congruence."""
    SOLVABLE_WITHIN_BUDGET = "SOLVABLE_WITHIN_BUDGET"
    SOLVABLE_EXCEEDS_BUDGET = "SOLVABLE_EXCEEDS_BUDGET"
    UNSOLVABLE = "UNSOLVABLE"


def parse_input(line: str) -> ProblemInput:
    """Parse a single line into ProblemInput."""
    tokens = line.split()
    if len(tokens) != 3:
        raise ValueError(f"Expected 3 tokens, got {len(tokens)}")
    b, d, a = int(tokens[0]), int(tokens[1]), int(tokens[2])
    return ProblemInput(b=b, d=d, a=a)


def _digit_count(n: int) -> int:
    """Return the number of decimal digits of a positive integer without str conversion."""
    if n <= 0:
        return 1
    # Use bit_length for a fast estimate, then refine
    bits = n.bit_length()
    # log10(2) ≈ 0.30103, so digits ≈ bits * 0.30103 + 1
    digits = int(bits * 0.30103) + 1
    # Refine: check if 10^(digits-1) <= n < 10^digits
    if 10**digits <= n:
        digits += 1
    elif digits > 1 and 10**(digits - 1) > n:
        digits -= 1
    return digits


def solve(b: int, d: int, a: int) -> int:
    """Return max n such that some k*b <= a has n trailing digits all equal to d."""
    answer = 0
    M = 10        # 10^n, starts at n=1
    T = d         # repdigit: d for n=1
    power = 1     # 10^(n-1), used for incremental T update
    max_n = _digit_count(a)
    k_max = a // b  # max k such that k*b <= a

    for n in range(1, max_n + 1):
        g = gcd(b, M)
        if T % g == 0:
            b_red = b // g
            M_red = M // g
            t_red = T // g
            k0 = (t_red * pow(b_red, -1, M_red)) % M_red
            if k0 == 0:
                k0 = M_red
            if k0 <= k_max:
                answer = n
        # Advance to next n
        power *= 10
        T += d * power
        M *= 10

    return answer


def main() -> None:
    """Entry point: read stdin, solve, print result."""
    line = input()
    p = parse_input(line)
    print(solve(p.b, p.d, p.a))


if __name__ == "__main__":
    main()
