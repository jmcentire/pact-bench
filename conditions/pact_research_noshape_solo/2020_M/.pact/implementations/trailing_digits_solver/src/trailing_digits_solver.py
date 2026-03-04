"""Trailing Digits Solver — finds the maximum consecutive trailing digit d
in any bundle price k*b <= a."""

import sys
from math import gcd
from dataclasses import dataclass
from typing import Optional

OptionalInt = Optional[int]


@dataclass
class ProblemInput:
    """The parsed and validated input triple for the trailing digits problem."""
    b: int
    d: int
    a: int


@dataclass
class CongruenceParams:
    """Internal parameters for the linear congruence at a given iteration n."""
    n: int
    modulus: int
    repdigit: int
    gcd_b_mod: int


def parse_input(raw_input: str) -> ProblemInput:
    """Parse stdin text into a validated ProblemInput."""
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)

    tokens = raw_input.split()
    if len(tokens) != 3:
        raise ValueError(f"Expected exactly 3 tokens, got {len(tokens)}")

    parsed = []
    for token in tokens:
        try:
            parsed.append(int(token))
        except ValueError:
            raise ValueError(f"Token '{token}' is not a valid integer")

    b, d, a = parsed

    if b < 1:
        raise ValueError(f"b must be >= 1, got {b}")
    if d < 0 or d > 9:
        raise ValueError(f"d must be in [0, 9], got {d}")
    if a < 1:
        raise ValueError(f"a must be >= 1, got {a}")

    return ProblemInput(b=b, d=d, a=a)


def min_multiple_with_n_trailing(
    b: int, d: int, n: int, modulus: int, repdigit: int
) -> OptionalInt:
    """Return the smallest positive multiple of b whose last n digits are all d,
    or None if no such multiple exists."""
    r = repdigit
    g = gcd(b, modulus)

    if r % g != 0:
        return None

    # Solve k * (b/g) ≡ (r/g) (mod modulus/g)
    reduced_b = b // g
    reduced_r = r // g
    reduced_mod = modulus // g

    inv = pow(reduced_b, -1, reduced_mod)
    k = (reduced_r * inv) % reduced_mod

    if k == 0:
        k = reduced_mod

    return k * b


def solve(b: int, d: int, a: int) -> int:
    """Return the maximum number of consecutive trailing digits d achievable
    in any positive multiple k*b <= a."""
    result = 0
    modulus = 1
    repdigit = 0

    n = 0
    while True:
        n += 1
        modulus *= 10
        repdigit = repdigit * 10 + d

        # If the repdigit itself exceeds a (and d != 0), no larger n can work either
        # For d == 0, repdigit stays 0, so we need a different bound
        if d != 0 and repdigit > a:
            break

        val = min_multiple_with_n_trailing(b, d, n, modulus, repdigit)
        if val is None:
            break
        if val > a:
            break
        result = n

        # Safety: if d == 0, check if modulus > a (the minimum qualifying
        # multiple for n+1 zeros would be at least modulus*10 which exceeds a)
        if d == 0 and modulus > a:
            break

    return result


def main() -> None:
    """Entry point: read b, d, a from stdin, print result."""
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)

    raw = sys.stdin.read()
    inp = parse_input(raw)
    result = solve(inp.b, inp.d, inp.a)
    print(result)


if __name__ == "__main__":
    main()
