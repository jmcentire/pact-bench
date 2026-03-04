# === Forever Young Solution (solution) v1 ===
# Implement a single Python script (solution.py) that reads two integers y and ℓ from stdin, and finds the largest base b such that y written in base b contains only decimal digits (0-9) and, when reinterpreted as a base-10 number, is at least ℓ. Uses a case-split by number of digits strategy: d=1 special case, d=2 enumeration, d=3 quadratic solving, d≥4 brute-force iteration. Base 10 is always valid as a fallback guarantee. Single module, Python 3.10+, standard library only, stdin/stdout I/O.

# Module invariants:
#   - Base 10 is always a valid base: for any y with 1 <= y <= 10^18, all digits of y in base 10 are in [0,9] and the reinterpretation equals y itself, so check_base(y, 10, ell) == True whenever ell <= y.
#   - The result of solve(y, ell) is always >= 10 due to the base-10 fallback guarantee.
#   - For d=2: y = a*b + c where a is the leading digit and c is the trailing digit, both in [0,9].
#   - For d=3: y = a*b^2 + c*b + e where a in [1,9], c in [0,9], e in [0,9].
#   - For d>=4: the maximum base to check is floor(y^(1/(d-1))), which is at most floor(y^(1/3)) ≈ 10^6 for y <= 10^18.
#   - to_base(y, b) always produces digits d_i where 0 <= d_i < b, and the leading digit d_0 > 0 for y > 0.
#   - The digit count d of y in base b satisfies b^(d-1) <= y < b^d.
#   - No external dependencies are used; only Python 3.10+ standard library (math.isqrt).
#   - The total number of candidate bases checked across all digit counts is bounded by approximately 10^6 + 990, ensuring the solution runs well under the time limit.

DigitList = list[int]
# A list of integer digits representing a number in some base, ordered most-significant digit first. Each element is a non-negative integer representing one digit position.

class SearchResult:
    """Result of searching for valid bases across a particular digit-count case or across all cases."""
    max_base: int                            # required, The largest valid base found. -1 if no valid base found in the searched range.
    found: bool                              # required, Whether at least one valid base was found in the searched range.

class CandidateBase:
    """A candidate base along with its digit decomposition and decimal reinterpretation, used during search."""
    base: int                                # required, range(base >= 2), The candidate base value, must be >= 2.
    digits: DigitList                        # required, The digits of y in this base, most-significant first.
    decimal_value: int                       # required, range(decimal_value >= 0), The value obtained by reinterpreting digits as a base-10 number.
    valid: bool                              # required, True if all digits are <= 9 and decimal_value >= ell.

def to_base(
    y: int,                    # range(y >= 0)
    b: int,                    # range(b >= 2)
) -> DigitList:
    """
    Convert a non-negative integer y to its representation in base b, returning digits as a list of integers ordered most-significant digit first. For y=0, returns [0].

    Preconditions:
      - y >= 0
      - b >= 2

    Postconditions:
      - len(result) >= 1
      - result[0] > 0 or (len(result) == 1 and result[0] == 0)
      - sum(result[i] * b**(len(result)-1-i) for i in range(len(result))) == y
      - all(0 <= d < b for d in result)

    Errors:
      - negative_y (ValueError): y < 0
          message: y must be non-negative
      - base_too_small (ValueError): b < 2
          message: Base must be at least 2

    Side effects: none
    Idempotent: yes
    """
    ...

def all_digits_valid(
    digits: DigitList,
) -> bool:
    """
    Check whether all digits in the given list are valid decimal digits, i.e., each digit is in the range [0, 9].

    Preconditions:
      - all(d >= 0 for d in digits)

    Postconditions:
      - result == all(0 <= d <= 9 for d in digits)

    Side effects: none
    Idempotent: yes
    """
    ...

def reinterpret_decimal(
    digits: DigitList,
) -> int:
    """
    Reinterpret a list of digits as a base-10 number. E.g., [1, 2, 3] becomes 123. Each digit must be in [0, 9] for the result to be meaningful, but this function does not enforce that constraint.

    Preconditions:
      - len(digits) >= 1

    Postconditions:
      - result == sum(digits[i] * 10**(len(digits)-1-i) for i in range(len(digits)))
      - result >= 0

    Errors:
      - empty_digits (ValueError): len(digits) == 0
          message: Digit list must not be empty

    Side effects: none
    Idempotent: yes
    """
    ...

def check_base(
    y: int,                    # range(y >= 0)
    b: int,                    # range(b >= 2)
    ell: int,                  # range(ell >= 1)
) -> bool:
    """
    For a given y and base b, convert y to base b, verify all digits are <= 9, reinterpret as base 10, and check that the reinterpreted value is >= ell. Returns True if and only if all conditions are satisfied.

    Preconditions:
      - y >= 0
      - b >= 2
      - ell >= 1

    Postconditions:
      - result == (all_digits_valid(to_base(y, b)) and reinterpret_decimal(to_base(y, b)) >= ell)

    Errors:
      - invalid_y (ValueError): y < 0
          message: y must be non-negative
      - invalid_base (ValueError): b < 2
          message: Base must be at least 2
      - invalid_ell (ValueError): ell < 1
          message: ell must be at least 1

    Side effects: none
    Idempotent: yes
    """
    ...

def int_nth_root(
    x: int,                    # range(x >= 0)
    n: int,                    # range(n >= 1)
) -> int:
    """
    Compute the integer n-th root of x, i.e., the largest integer r such that r^n <= x. Uses math.isqrt for n=2 and Newton's method with integer arithmetic for general n. Handles edge cases for x=0 and x=1.

    Preconditions:
      - x >= 0
      - n >= 1

    Postconditions:
      - result >= 0
      - result ** n <= x
      - (result + 1) ** n > x

    Errors:
      - negative_x (ValueError): x < 0
          message: x must be non-negative
      - zero_degree (ValueError): n < 1
          message: Root degree must be at least 1

    Side effects: none
    Idempotent: yes
    """
    ...

def search_d1(
    y: int,                    # range(y >= 0)
    ell: int,                  # range(ell >= 1)
) -> SearchResult:
    """
    Handle the d=1 special case. If y is a single digit (0 <= y <= 9) and y >= ell, then any base b > y is valid. In this case the answer is unbounded — return a very large sentinel value (e.g., y+1 or per problem constraints). If y > 9 or y < ell, no single-digit representation satisfies both conditions.

    Preconditions:
      - y >= 0
      - ell >= 1

    Postconditions:
      - If y <= 9 and y >= ell then result.found == True and result.max_base is a large sentinel (e.g., 10**18 + 1)
      - If y > 9 or y < ell then result.found == False and result.max_base == -1

    Side effects: none
    Idempotent: yes
    """
    ...

def search_d2(
    y: int,                    # range(y >= 0)
    ell: int,                  # range(ell >= 1)
) -> SearchResult:
    """
    Search for the largest base b producing a 2-digit representation of y where both digits are in [0,9] and the 2-digit decimal reinterpretation is >= ell. Enumerates all (a, c) pairs with a in [1,9] and c in [0,9], computes b = (y - c) / a, and verifies: b is a positive integer >= 2, b > max(a, c) (ensures exactly 2 digits), b <= y (ensures representation is not 1 digit), and 10*a + c >= ell.

    Preconditions:
      - y >= 0
      - ell >= 1

    Postconditions:
      - If result.found, then result.max_base >= 2
      - If result.found, then to_base(y, result.max_base) has length 2
      - If result.found, then check_base(y, result.max_base, ell) == True
      - If result.found, then no valid base b > result.max_base produces a 2-digit representation satisfying the constraints

    Side effects: none
    Idempotent: yes
    """
    ...

def search_d3(
    y: int,                    # range(y >= 0)
    ell: int,                  # range(ell >= 1)
) -> SearchResult:
    """
    Search for the largest base b producing a 3-digit representation of y where all digits are in [0,9] and the 3-digit decimal reinterpretation is >= ell. Enumerates all (a, c, e) triples with a in [1,9] and c,e in [0,9]. For each triple, solves a*b^2 + c*b + e = y using the quadratic formula with integer square root (discriminant = c^2 - 4*a*(e - y), b = (-c + isqrt(disc)) / (2*a)). Verifies b is a positive integer >= 2, produces exactly 3 digits, and 100*a + 10*c + e >= ell.

    Preconditions:
      - y >= 0
      - ell >= 1

    Postconditions:
      - If result.found, then result.max_base >= 2
      - If result.found, then to_base(y, result.max_base) has length 3
      - If result.found, then check_base(y, result.max_base, ell) == True
      - If result.found, then no valid base b > result.max_base produces a 3-digit representation satisfying the constraints

    Side effects: none
    Idempotent: yes
    """
    ...

def search_d_ge_4(
    y: int,                    # range(y >= 0)
    ell: int,                  # range(ell >= 1)
) -> SearchResult:
    """
    Search for the largest base b producing a d-digit representation (d >= 4) of y where all digits are in [0,9] and the decimal reinterpretation is >= ell. Iterates d from 4 up to ~60 (until the base range becomes empty). For each d, iterates bases b from 2 to floor(y^(1/(d-1))). For each (d, b) pair, calls check_base. Tracks the maximum valid base found.

    Preconditions:
      - y >= 0
      - ell >= 1

    Postconditions:
      - If result.found, then result.max_base >= 2
      - If result.found, then len(to_base(y, result.max_base)) >= 4
      - If result.found, then check_base(y, result.max_base, ell) == True

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    y: int,                    # range(1 <= y <= 10**18)
    ell: int,                  # range(1 <= ell <= y)
) -> int:
    """
    Main solver function. Given y and ell, finds the largest base b >= 2 such that y written in base b has all digits <= 9 and the base-10 reinterpretation of those digits is >= ell. Runs all digit-count search cases (d=1, d=2, d=3, d>=4), collects results, and returns the overall maximum valid base. Base 10 is always a valid fallback since y in base 10 is y itself, and the problem guarantees y >= ell.

    Preconditions:
      - 1 <= y <= 10**18
      - 1 <= ell <= y

    Postconditions:
      - result >= 2
      - result >= 10 (base 10 is always valid as fallback)
      - check_base(y, result, ell) == True
      - For all b > result: check_base(y, b, ell) == False (unless result is sentinel for unbounded case)

    Errors:
      - y_out_of_range (ValueError): y < 1 or y > 10**18
          message: y must be between 1 and 10^18 inclusive
      - ell_out_of_range (ValueError): ell < 1 or ell > y
          message: ell must be between 1 and y inclusive

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point. Reads two space-separated integers y and ell from stdin, calls solve(y, ell), and writes the result to stdout followed by a newline. Handles exactly one test case per invocation.

    Preconditions:
      - stdin contains exactly one line with two space-separated integers y and ell
      - 1 <= ell <= y <= 10^18

    Postconditions:
      - stdout contains exactly one line with the integer result followed by a newline
      - The output integer is the largest valid base b >= 2 satisfying the problem constraints

    Errors:
      - malformed_input (ValueError): stdin does not contain two valid space-separated integers
          message: Expected two space-separated integers on stdin
      - eof (EOFError): stdin is empty or EOF reached before reading input
          message: No input available on stdin

    Side effects: Reads from stdin, Writes to stdout
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['DigitList', 'SearchResult', 'CandidateBase', 'to_base', 'all_digits_valid', 'reinterpret_decimal', 'check_base', 'int_nth_root', 'search_d1', 'search_d2', 'search_d3', 'search_d_ge_4', 'solve', 'main', 'EOFError']
