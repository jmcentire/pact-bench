import math
from enum import Enum
from typing import Optional

DigitList = list[int]
OptionalDigitList = Optional[DigitList]


class Phase(Enum):
    TWO_DIGIT_ALGEBRAIC = "TWO_DIGIT_ALGEBRAIC"
    THREE_DIGIT_QUADRATIC = "THREE_DIGIT_QUADRATIC"
    FOUR_PLUS_DIGIT_ENUMERATION = "FOUR_PLUS_DIGIT_ENUMERATION"
    FALLBACK_BASE_10 = "FALLBACK_BASE_10"


def main() -> None:
    y, l = map(int, input().split())
    print(solve(y, l))


def solve(y: int, l: int) -> int:
    if l < 2 or y < l:
        raise ValueError(f"Constraint violation: need 2 <= l <= y, got y={y}, l={l}")

    best = 10  # Phase 4: base 10 always works

    b1 = solve_phase1_two_digit(y, l)
    if b1 > best:
        best = b1

    b2 = solve_phase2_three_digit(y, l)
    if b2 > best:
        best = b2

    b3 = solve_phase3_four_plus_digit(y, l)
    if b3 > best:
        best = b3

    return best


def to_base(y: int, b: int) -> OptionalDigitList:
    if b < 2:
        raise ValueError(f"Invalid base: {b}")
    if y < 0:
        raise ValueError(f"Negative input: {y}")
    if y == 0:
        return [0]
    digits = []
    n = y
    while n > 0:
        d = n % b
        if d >= 10:
            return None
        digits.append(d)
        n //= b
    digits.reverse()
    return digits


def reinterpret_base10(digits: DigitList) -> int:
    if not digits:
        raise ValueError("Empty digits list")
    result = 0
    for d in digits:
        if d < 0 or d > 9:
            raise ValueError(f"Digit out of range: {d}")
        result = result * 10 + d
    return result


def integer_kth_root(n: int, k: int) -> int:
    if n < 0:
        raise ValueError(f"Negative n: {n}")
    if k < 1:
        raise ValueError(f"Invalid k: {k}")
    if n == 0:
        return 0
    if k == 1:
        return n
    if k == 2:
        return math.isqrt(n)

    # Float estimate, then adjust with integer arithmetic
    r = int(round(n ** (1.0 / k)))
    # Clamp to avoid huge computations on wildly wrong estimates
    if r < 0:
        r = 0
    # Adjust down if too large
    while r > 0 and r ** k > n:
        r -= 1
    # Adjust up if too small
    while (r + 1) ** k <= n:
        r += 1
    return r


def solve_phase1_two_digit(y: int, l: int) -> int:
    best = 0
    for a in range(1, 10):
        for c in range(0, 10):
            if 10 * a + c < l:
                continue
            remainder = y - c
            if remainder <= 0:
                continue
            if remainder % a != 0:
                continue
            b = remainder // a
            if b < 11:
                continue
            if b <= max(a, c):
                continue
            if b > best:
                best = b
    return best


def solve_phase2_three_digit(y: int, l: int) -> int:
    best = 0
    for a in range(1, 10):
        for d in range(0, 10):
            for e in range(0, 10):
                val = 100 * a + 10 * d + e
                if val < l:
                    continue
                # Solve a*b^2 + d*b + (e - y) = 0
                # discriminant = d^2 + 4*a*(y - e)
                diff = y - e
                if diff < 0:
                    continue
                disc = d * d + 4 * a * diff
                sqrt_disc = math.isqrt(disc)
                if sqrt_disc * sqrt_disc != disc:
                    continue
                # b = (-d + sqrt_disc) / (2*a)
                num = -d + sqrt_disc
                if num <= 0:
                    continue
                denom = 2 * a
                if num % denom != 0:
                    continue
                b = num // denom
                if b < 11:
                    continue
                if b <= max(a, d, e):
                    continue
                # Verify reconstruction
                if a * b * b + d * b + e == y:
                    if b > best:
                        best = b
    return best


def solve_phase3_four_plus_digit(y: int, l: int) -> int:
    best = 0
    # For k >= 4 digits in base b: b^3 <= y, so b <= y^(1/3)
    upper = integer_kth_root(y, 3)
    if upper < 11:
        return 0
    for b in range(upper, 10, -1):
        if b <= best:
            break
        digits = to_base(y, b)
        if digits is not None and len(digits) >= 4:
            if reinterpret_base10(digits) >= l:
                best = b
                break  # Iterating high to low, first valid is largest
    return best


if __name__ == "__main__":
    main()
