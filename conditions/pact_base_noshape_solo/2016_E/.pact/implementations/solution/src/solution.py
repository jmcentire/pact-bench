"""Forever Young solution: find the largest base b such that y in base b
has only decimal digits and reinterpreted as base-10 is >= ell."""

import sys
import math

DigitList = list[int]


class SearchResult:
    """Result of searching for valid bases."""
    def __init__(self, max_base: int, found: bool):
        self.max_base = max_base
        self.found = found


class CandidateBase:
    """A candidate base with digit decomposition and decimal reinterpretation."""
    def __init__(self, base: int, digits: DigitList, decimal_value: int, valid: bool):
        self.base = base
        self.digits = digits
        self.decimal_value = decimal_value
        self.valid = valid


def to_base(y: int, b: int) -> DigitList:
    if y < 0:
        raise ValueError("y must be non-negative")
    if b < 2:
        raise ValueError("Base must be at least 2")
    if y == 0:
        return [0]
    digits = []
    while y > 0:
        digits.append(y % b)
        y //= b
    digits.reverse()
    return digits


def all_digits_valid(digits: DigitList) -> bool:
    return all(0 <= d <= 9 for d in digits)


def reinterpret_decimal(digits: DigitList) -> int:
    if len(digits) == 0:
        raise ValueError("Digit list must not be empty")
    result = 0
    for d in digits:
        result = result * 10 + d
    return result


def check_base(y: int, b: int, ell: int) -> bool:
    if y < 0:
        raise ValueError("y must be non-negative")
    if b < 2:
        raise ValueError("Base must be at least 2")
    if ell < 1:
        raise ValueError("ell must be at least 1")
    digits = to_base(y, b)
    if not all_digits_valid(digits):
        return False
    return reinterpret_decimal(digits) >= ell


def int_nth_root(x: int, n: int) -> int:
    if x < 0:
        raise ValueError("x must be non-negative")
    if n < 1:
        raise ValueError("Root degree must be at least 1")
    if n == 1:
        return x
    if x == 0:
        return 0
    if n == 2:
        return math.isqrt(x)
    # Newton's method for integer nth root
    # Initial guess using floating point
    guess = int(round(x ** (1.0 / n)))
    # Adjust guess to be safe (floating point can be off by a few)
    # Search around the guess
    guess = max(guess, 1)
    # Make sure guess^n doesn't overflow too badly; clamp
    # Refine with Newton's method
    r = guess
    while True:
        # r_new = ((n-1)*r + x // r^(n-1)) // n
        rn1 = r ** (n - 1)
        if rn1 == 0:
            r += 1
            continue
        r_new = ((n - 1) * r + x // rn1) // n
        if r_new >= r:
            break
        r = r_new
    # r might be slightly off; adjust
    while (r + 1) ** n <= x:
        r += 1
    while r > 0 and r ** n > x:
        r -= 1
    return r


def search_d1(y: int, ell: int) -> SearchResult:
    if y <= 9 and y >= ell:
        return SearchResult(max_base=10**18 + 1, found=True)
    return SearchResult(max_base=-1, found=False)


def search_d2(y: int, ell: int) -> SearchResult:
    best = -1
    for a in range(1, 10):
        for c in range(0, 10):
            remainder = y - c
            if remainder <= 0:
                continue
            if remainder % a != 0:
                continue
            b = remainder // a
            if b < 2:
                continue
            # Ensure exactly 2 digits: need a < b and c < b
            if a >= b or c >= b:
                continue
            # Check decimal reinterpretation
            decimal_val = 10 * a + c
            if decimal_val >= ell:
                if b > best:
                    best = b
    if best >= 2:
        return SearchResult(max_base=best, found=True)
    return SearchResult(max_base=-1, found=False)


def search_d3(y: int, ell: int) -> SearchResult:
    best = -1
    for a in range(1, 10):
        for c in range(0, 10):
            for e in range(0, 10):
                decimal_val = 100 * a + 10 * c + e
                if decimal_val < ell:
                    continue
                # Solve a*b^2 + c*b + e = y
                # a*b^2 + c*b + (e - y) = 0
                # disc = c^2 - 4*a*(e - y) = c^2 + 4*a*(y - e)
                disc = c * c + 4 * a * (y - e)
                if disc < 0:
                    continue
                sqrt_disc = math.isqrt(disc)
                if sqrt_disc * sqrt_disc != disc:
                    continue
                # b = (-c + sqrt_disc) / (2*a)
                numerator = -c + sqrt_disc
                if numerator <= 0:
                    continue
                denom = 2 * a
                if numerator % denom != 0:
                    continue
                b = numerator // denom
                if b < 2:
                    continue
                # Ensure exactly 3 digits: a < b, c < b, e < b
                if a >= b or c >= b or e >= b:
                    continue
                # Verify (floating point sqrt might be wrong for huge numbers)
                if a * b * b + c * b + e != y:
                    continue
                if b > best:
                    best = b
    if best >= 2:
        return SearchResult(max_base=best, found=True)
    return SearchResult(max_base=-1, found=False)


def search_d_ge_4(y: int, ell: int) -> SearchResult:
    best = -1
    # For d >= 4 digits in base b: b^3 <= y, so b <= y^(1/3)
    max_b = int_nth_root(y, 3)
    for b in range(2, max_b + 1):
        digits = to_base(y, b)
        if len(digits) < 4:
            continue
        if not all_digits_valid(digits):
            continue
        if reinterpret_decimal(digits) >= ell:
            if b > best:
                best = b
    if best >= 2:
        return SearchResult(max_base=best, found=True)
    return SearchResult(max_base=-1, found=False)


def solve(y: int, ell: int) -> int:
    if y < 1 or y > 10**18:
        raise ValueError("y must be between 1 and 10^18 inclusive")
    if ell < 1 or ell > y:
        raise ValueError("ell must be between 1 and y inclusive")

    results = [
        search_d1(y, ell),
        search_d2(y, ell),
        search_d3(y, ell),
        search_d_ge_4(y, ell),
    ]

    best = 10  # base 10 is always valid fallback
    for r in results:
        if r.found and r.max_base > best:
            best = r.max_base
    return best


def main() -> None:
    line = sys.stdin.readline()
    if not line:
        raise EOFError("No input available on stdin")
    parts = line.split()
    if len(parts) != 2:
        raise ValueError("Expected two space-separated integers on stdin")
    try:
        y, ell = int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError("Expected two space-separated integers on stdin")
    result = solve(y, ell)
    print(result)


if __name__ == "__main__":
    main()
