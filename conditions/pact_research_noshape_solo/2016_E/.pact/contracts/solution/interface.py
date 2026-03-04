# === Forever Young Solution (solution) v1 ===
# Implement a single Python script (solution.py) that reads y and l from stdin, and finds the largest base b such that y written in base b contains only decimal digits (0-9) and, when interpreted as a base-10 number, is at least l. Uses a hybrid algorithmic approach: algebraic solution for 2-digit representations, quadratic solve for 3-digit representations, enumeration for 4+ digit representations, with base 10 as a guaranteed fallback. Python 3.10+, standard library only. Reads from stdin, writes to stdout.

# Module invariants:
#   - Base 10 is always a valid answer: y in base 10 is y itself, and y >= l by problem constraints, so solve(y, l) >= 10
#   - For any valid base b, every digit of y in base b must be in [0, 9], i.e., b must be > max digit (which is at most 9), so b >= 11 or b == 10
#   - The answer base b satisfies b >= 10 and b <= y (since y in base y+1 is just 'y' which is a single digit >= 2, and for b > y the representation is also single-digit)
#   - For k=2 representation y = a*b + c: a >= 1 and a <= 9 and c >= 0 and c <= 9 and b > max(a, c)
#   - For k=3 representation y = a*b^2 + d*b + e: a >= 1 and a <= 9 and d >= 0 and d <= 9 and e >= 0 and e <= 9 and b > max(a, d, e)
#   - All intermediate arithmetic uses Python arbitrary-precision integers to avoid overflow for y up to 10^18
#   - integer_kth_root(n, k) returns r such that r^k <= n < (r+1)^k — this is exact with no floating-point error

int = primitive  # Python integer (arbitrary precision)

str = primitive  # Python string

bool = primitive  # Python boolean

None = primitive  # Python None type

DigitList = list[int]
# A list of integer digits representing a number in some base, most significant digit first. Each element is a non-negative integer. For valid base-b representations with only decimal-compatible digits, each element is in [0, 9].

OptionalDigitList = DigitList | None

class Phase(Enum):
    """Enumeration of the algorithmic phases used in the solve function."""
    TWO_DIGIT_ALGEBRAIC = "TWO_DIGIT_ALGEBRAIC"
    THREE_DIGIT_QUADRATIC = "THREE_DIGIT_QUADRATIC"
    FOUR_PLUS_DIGIT_ENUMERATION = "FOUR_PLUS_DIGIT_ENUMERATION"
    FALLBACK_BASE_10 = "FALLBACK_BASE_10"

def main() -> None:
    """
    Entry point. Reads two space-separated integers y and l from stdin, calls solve(y, l), and prints the result to stdout followed by a newline. This is the top-level function invoked when the script is run.

    Preconditions:
      - stdin contains exactly one line with two space-separated integers y and l
      - y and l satisfy problem constraints: 2 <= l <= y <= 10^18

    Postconditions:
      - Exactly one integer is printed to stdout followed by a newline
      - The printed integer is the largest valid base b >= 10 such that y in base b has only digits 0-9 and the base-10 reinterpretation is >= l

    Errors:
      - invalid_input_format (ValueError): stdin does not contain exactly two space-separated integers
      - eof_on_stdin (EOFError): stdin is empty or closed before input can be read

    Side effects: Reads from stdin, Writes to stdout
    Idempotent: yes
    """
    ...

def solve(
    y: int,                    # range(2 <= y <= 10**18)
    l: int,                    # range(2 <= l <= y)
) -> int:
    """
    Core solver. Finds the largest base b (b >= 10) such that y written in base b contains only digits 0-9 and, when those digits are reinterpreted as a base-10 number, the result is >= l. Implements a four-phase hybrid algorithm: Phase 1 (k=2, algebraic), Phase 2 (k=3, quadratic), Phase 3 (k>=4, enumeration), Phase 4 (fallback to base 10). Returns the maximum valid base found across all phases.

    Preconditions:
      - 2 <= l <= y <= 10^18

    Postconditions:
      - returned value b >= 10
      - to_base(y, b) is not None (all digits are in [0, 9])
      - reinterpret_base10(to_base(y, b)) >= l
      - No base b' > b exists such that to_base(y, b') is not None and reinterpret_base10(to_base(y, b')) >= l

    Errors:
      - constraint_violation (ValueError): y or l are outside the valid range (2 <= l <= y <= 10^18)

    Side effects: none
    Idempotent: yes
    """
    ...

def to_base(
    y: int,                    # range(y >= 0)
    b: int,                    # range(b >= 2)
) -> OptionalDigitList:
    """
    Converts the non-negative integer y into its base-b digit representation (most significant digit first). If any digit in the representation is >= 10, returns None immediately (early termination). Otherwise returns the list of digits.

    Preconditions:
      - y >= 0
      - b >= 2

    Postconditions:
      - If result is not None, then result is a non-empty list of ints each in [0, 9]
      - If result is not None, then sum(d * b^(len(result)-1-i) for i, d in enumerate(result)) == y
      - If result is not None, then result[0] != 0 (no leading zeros) unless y == 0 in which case result == [0]
      - If result is None, then at least one digit of y in base b is >= 10

    Errors:
      - invalid_base (ValueError): b < 2
      - negative_input (ValueError): y < 0

    Side effects: none
    Idempotent: yes
    """
    ...

def reinterpret_base10(
    digits: DigitList,         # custom(len(digits) > 0 and all(0 <= d <= 9 for d in digits))
) -> int:
    """
    Takes a list of digits (most significant first) and interprets them as a base-10 number. For example, [1, 2, 3] -> 123. The digits are assumed to be valid (each in [0, 9]).

    Preconditions:
      - digits is non-empty
      - All elements of digits are in [0, 9]

    Postconditions:
      - returned value == sum(d * 10^(len(digits)-1-i) for i, d in enumerate(digits))
      - returned value >= 0

    Errors:
      - empty_digits (ValueError): digits list is empty
      - digit_out_of_range (ValueError): Any digit is not in [0, 9]

    Side effects: none
    Idempotent: yes
    """
    ...

def integer_kth_root(
    n: int,                    # range(n >= 0)
    k: int,                    # range(k >= 1)
) -> int:
    """
    Computes floor(n^(1/k)) exactly using integer arithmetic. Returns the largest integer r such that r^k <= n. Uses Newton's method with integer arithmetic and careful convergence checking to avoid floating-point inaccuracies for large n (up to 10^18).

    Preconditions:
      - n >= 0
      - k >= 1

    Postconditions:
      - returned value r >= 0
      - r^k <= n
      - (r+1)^k > n

    Errors:
      - negative_n (ValueError): n < 0
      - invalid_k (ValueError): k < 1

    Side effects: none
    Idempotent: yes
    """
    ...

def solve_phase1_two_digit(
    y: int,
    l: int,
) -> int:
    """
    Phase 1 (k=2, algebraic): Finds the largest base b >= 11 such that y in base b is a 2-digit number (y = a*b + c, with a in [1,9], c in [0,9]) and 10*a + c >= l. Iterates over all 90 possible (a, c) pairs, computes b = (y - c) / a if divisible, verifies b > max(a, c) and b >= 11, and tracks the maximum valid b. Returns the best base found, or 0 if no valid 2-digit base exists.

    Preconditions:
      - 2 <= l <= y <= 10^18

    Postconditions:
      - returned value is 0 or >= 11
      - If returned value b > 0: y = a*b + c for some a in [1,9], c in [0,9], and 10*a+c >= l, and b > max(a,c)
      - If returned value is 0: no valid 2-digit base >= 11 exists for the given y and l

    Side effects: none
    Idempotent: yes
    """
    ...

def solve_phase2_three_digit(
    y: int,
    l: int,
) -> int:
    """
    Phase 2 (k=3, quadratic): Finds the largest base b >= 11 such that y in base b is a 3-digit number (y = a*b^2 + d*b + e, with a in [1,9], d in [0,9], e in [0,9]) and 100*a + 10*d + e >= l. For each (a, d, e) triple, solves the quadratic a*b^2 + d*b + (e - y) = 0 using the discriminant and math.isqrt for exact integer square root. Verifies b is a positive integer > max(a,d,e,10). Returns the best base found, or 0 if no valid 3-digit base exists.

    Preconditions:
      - 2 <= l <= y <= 10^18

    Postconditions:
      - returned value is 0 or >= 11
      - If returned value b > 0: y = a*b^2 + d*b + e for some a in [1,9], d in [0,9], e in [0,9], and 100*a+10*d+e >= l, and b > max(a,d,e)
      - If returned value is 0: no valid 3-digit base >= 11 exists for the given y and l

    Side effects: none
    Idempotent: yes
    """
    ...

def solve_phase3_four_plus_digit(
    y: int,
    l: int,
) -> int:
    """
    Phase 3 (k>=4, enumeration): For each digit count k from 4 upward, computes the valid base range [integer_kth_root(y, k), integer_kth_root(y, k-1)] and iterates bases from high to low. For each base, converts y to base b using to_base, checks all digits are in [0,9], and verifies reinterpret_base10 >= l. Returns the best base found across all k >= 4, or 0 if none. Stops increasing k when the base range upper bound drops below 11.

    Preconditions:
      - 2 <= l <= y <= 10^18

    Postconditions:
      - returned value is 0 or >= 11
      - If returned value b > 0: to_base(y, b) is not None and len(to_base(y, b)) >= 4 and reinterpret_base10(to_base(y, b)) >= l
      - If returned value is 0: no valid base b >= 11 produces a representation of y with 4 or more digits that are all in [0,9] with base-10 reinterpretation >= l

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['DigitList', 'OptionalDigitList', 'Phase', 'main', 'EOFError', 'solve', 'to_base', 'reinterpret_base10', 'integer_kth_root', 'solve_phase1_two_digit', 'solve_phase2_three_digit', 'solve_phase3_four_plus_digit']
