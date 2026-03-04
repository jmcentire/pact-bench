# === Trailing Digits Solver (trailing_digits_solver) v1 ===
# A single Python 3.10+ module that solves the Trailing Digits problem. Reads b, d, a from stdin and outputs the maximum number of consecutive trailing digits d achievable in a bundle price k*b ≤ a. Uses an iterative approach incrementing n from 1 upward, checking modular congruence solvability via gcd and modular inverse at each step. Handles arbitrarily large a (up to 10^10000) using Python native big integers. Standard library only (~30-40 lines, single file with __main__ guard).

# Module invariants:
#   - M is always equal to 10^n at the start of each loop iteration for the current n
#   - T_n is always equal to d * (10^n - 1) / 9, i.e., n repetitions of digit d (e.g., d=4, n=3 → T_n=444); when d=0, T_n=0 for all n
#   - T_n is maintained incrementally: T_{n+1} = T_n + d * 10^n (equivalently, T is updated as T += d * prev_power where prev_power tracks 10^(n-1))
#   - M is maintained incrementally: M_{n+1} = M_n * 10
#   - The answer variable is monotonically non-decreasing during the loop (once n is achievable, all smaller values remain achievable, though the answer only tracks the maximum)
#   - g = gcd(b, M) divides both b and M, ensuring the reduced congruence b'*k ≡ T' (mod M') has gcd(b', M') = 1, guaranteeing the modular inverse exists when T_n % g == 0
#   - k0 is always the smallest positive integer satisfying k*b ≡ T_n (mod M), so k0*b is the smallest positive multiple of b with the desired n trailing digits
#   - All intermediate values are Python ints — no floating point is ever used
#   - The loop terminates after at most len(str(a)) iterations because n cannot exceed the total number of digits in a (k*b <= a implies k*b has at most len(str(a)) digits)
#   - The program uses only Python standard library (math.gcd, built-in pow with three arguments for modular inverse)

int = primitive  # Python arbitrary-precision integer. All intermediate values (b, d, a, M, T_n, g, k0, answer) are ints. Python natively handles integers with thousands of digits.

str = primitive  # Python string type, used for raw stdin line reading.

None = primitive  # Python None type, used as return type for main() since it communicates via stdout.

class ProblemInput:
    """Parsed input for the Trailing Digits problem. Represents the three integers read from a single stdin line."""
    b: int                                   # required, range(1 <= b <= 10**9), Bundle price — the base multiplier. Every candidate price is a positive multiple of b.
    d: int                                   # required, range(0 <= d <= 9), Target trailing digit (0-9). We seek multiples of b whose trailing digits are all d.
    a: int                                   # required, range(1 <= a), custom(len(str(a)) <= 10001), Budget — maximum allowable value for k*b. Can be astronomically large (up to 10^10000). Must be read as Python int from string to preserve precision.

class CongruenceResult(Enum):
    """Outcome of attempting to solve the modular congruence k*b ≡ T_n (mod 10^n) for a given n."""
    SOLVABLE_WITHIN_BUDGET = "SOLVABLE_WITHIN_BUDGET"
    SOLVABLE_EXCEEDS_BUDGET = "SOLVABLE_EXCEEDS_BUDGET"
    UNSOLVABLE = "UNSOLVABLE"

def main() -> None:
    """
    Entry point. Reads one line from stdin containing three space-separated integers b, d, a. Computes and prints to stdout the maximum number of consecutive trailing digits d achievable in any positive multiple k*b where k*b ≤ a. Prints 0 if no multiple of b within budget ends in digit d. This function orchestrates parsing, the core algorithm loop, and output.

    Preconditions:
      - stdin contains exactly one line with three space-separated non-negative integers
      - First integer b satisfies 1 <= b <= 10^9
      - Second integer d satisfies 0 <= d <= 9
      - Third integer a satisfies 1 <= a <= 10^10000

    Postconditions:
      - Exactly one line is printed to stdout containing a single non-negative integer
      - The printed integer n is the maximum value such that there exists a positive integer k where k*b <= a and the last n digits of k*b are all equal to d
      - If no positive multiple of b within budget [b, 2b, ..., floor(a/b)*b] has its last digit equal to d, the output is 0
      - Output n satisfies 0 <= n <= len(str(a))
      - Output is followed by a newline character (Python print default)

    Errors:
      - malformed_input (ValueError): stdin line does not contain exactly three space-separated integers
          note: Per competitive programming convention, input is trusted to conform to constraints. No explicit error handling is implemented; Python will raise ValueError or IndexError naturally on malformed input.
      - empty_stdin (EOFError): stdin is empty or EOF reached before reading a line
          note: Raised by input() if no data available on stdin.

    Side effects: none
    Idempotent: yes
    """
    ...

def parse_input(
    line: str,                 # custom(len(line.split()) == 3 and all(tok.isdigit() or (tok[0]=='-' and tok[1:].isdigit()) for tok in line.split()))
) -> ProblemInput:
    """
    Reads a single line from stdin and parses it into the three problem parameters b, d, a. Returns them as a ProblemInput struct. This is a logical sub-step of main(); in the actual single-file implementation it may be inlined, but the contract specifies it as a distinct logical function for clarity.

    Preconditions:
      - line contains exactly three space-separated tokens that are valid integer representations
      - Parsed b satisfies 1 <= b <= 10^9
      - Parsed d satisfies 0 <= d <= 9
      - Parsed a satisfies 1 <= a <= 10^10000

    Postconditions:
      - Returned ProblemInput.b == int(line.split()[0])
      - Returned ProblemInput.d == int(line.split()[1])
      - Returned ProblemInput.a == int(line.split()[2])
      - All three fields are Python ints with correct values

    Errors:
      - wrong_token_count (ValueError): line.split() does not yield exactly 3 tokens
          detail: Expected exactly 3 space-separated integers on the input line.
      - non_integer_token (ValueError): Any of the three tokens cannot be parsed as a Python int
          detail: All three tokens must be valid integer literals.

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    b: int,                    # range(1 <= b <= 10**9)
    d: int,                    # range(0 <= d <= 9)
    a: int,                    # range(a >= 1)
) -> int:
    """
    Core algorithm. Given b, d, a, computes the maximum number of consecutive trailing digits d achievable in any positive multiple k*b ≤ a. Iterates n from 1 upward (up to len(str(a)) digits), maintaining M=10^n and T_n incrementally. For each n: computes g=gcd(b, M), checks if T_n is divisible by g (solvability condition), reduces the congruence to find the smallest positive k via modular inverse pow(b', -1, M'), and verifies k*b ≤ a. Tracks and returns the maximum achievable n.

    Preconditions:
      - 1 <= b <= 10^9
      - 0 <= d <= 9
      - a >= 1
      - a >= b (implicitly required for any solution to exist with k >= 1; if a < b, answer is 0)

    Postconditions:
      - Returned value n satisfies 0 <= n <= len(str(a))
      - If n > 0, there exists a positive integer k such that k*b <= a and (k*b) mod 10^n == d * (10^n - 1) / 9 (i.e., last n digits are all d)
      - For all m where n < m <= len(str(a)), no positive integer k exists such that k*b <= a and (k*b) mod 10^m == d * (10^m - 1) / 9
      - If n == 0, no positive multiple of b within [1, a] has its units digit equal to d
      - Special case: when d == 0, T_n == 0 for all n, meaning we seek k*b divisible by 10^n

    Errors:
      - modular_inverse_does_not_exist (ValueError): gcd(b // g, M // g) != 1 after reduction — this should never happen because g = gcd(b, M) ensures the reduced values are coprime, but is listed for completeness
          detail: Internal error: reduced b' and M' are not coprime. This indicates a bug in the gcd reduction step.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ProblemInput', 'CongruenceResult', 'main', 'EOFError', 'parse_input', 'solve']
