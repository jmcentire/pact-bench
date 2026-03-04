# === Fibonacci Words Solution (fibonacci_words) v1 ===
# A single Python file (solution.py) that reads EOF-terminated input of test cases (alternating lines: n then pattern p) and counts overlapping occurrences of p in F(n). F(0)="0", F(1)="1", F(k)=F(k-1)+F(k-2) for k>=2. Uses KMP for overlapping pattern matching and a bottom-up DP recurrence that tracks count, prefix, and suffix of each Fibonacci word to avoid materializing exponentially large strings.

# Module invariants:
#   - F(0) = '0', F(1) = '1', F(k) = F(k-1) + F(k-2) for k >= 2 (string concatenation)
#   - fib_len[0] = 1, fib_len[1] = 1, fib_len[k] = fib_len[k-1] + fib_len[k-2]; tracked with a cap at len(pattern)+1 to avoid unnecessary large integer arithmetic for length tracking
#   - For all k in [0..n]: len(FibState[k].prefix) == min(fib_len[k], len(pattern) - 1)
#   - For all k in [0..n]: len(FibState[k].suffix) == min(fib_len[k], len(pattern) - 1)
#   - For all k in [0..n]: FibState[k].count >= 0
#   - For all k >= 2: FibState[k].count == FibState[k-1].count + FibState[k-2].count + cross_matches(k)
#   - cross_matches(k) == count_overlapping(suffix[k-1] + prefix[k-2], pattern, failure) - count_overlapping(suffix[k-1], pattern, failure) - count_overlapping(prefix[k-2], pattern, failure)
#   - For all k in [0..n]: FibState[k].prefix is the first min(fib_len[k], len(pattern)-1) characters of F(k)
#   - For all k in [0..n]: FibState[k].suffix is the last min(fib_len[k], len(pattern)-1) characters of F(k)
#   - Overlapping occurrences are counted: if pattern appears at positions i and i+1, both are counted
#   - The KMP failure table satisfies: failure[0] == 0 and for all i: failure[i] < i+1 and pattern[0:failure[i]] == pattern[i-failure[i]+1:i+1]
#   - Only DP states for k-1 and k-2 need to be retained at any time (space optimization is permitted but not required)
#   - Output format is exactly 'Case {i}: {count}\n' for 1-indexed test case i with no leading zeros in count and no trailing spaces

int = primitive  # Python arbitrary-precision integer. Results may be up to 2^63-1 or larger.

str = primitive  # Python string. Used for patterns and prefix/suffix fragments.

bool = primitive  # Python boolean.

None = primitive  # Python None type, used as void return.

FailureTable = list[int]
# KMP failure/prefix function table. FailureTable[i] is the length of the longest proper prefix of pattern[0..i] that is also a suffix. Length equals len(pattern).

class FibState:
    """Memoized state for F(k) relative to a given pattern p. Represents the accumulated occurrence count and the boundary fragments needed for cross-boundary matching at the next DP level. This is a NamedTuple with three fields."""
    count: int                               # required, Total number of overlapping occurrences of pattern p in F(k). Non-negative.
    prefix: str                              # required, Leading fragment of F(k) of length min(fib_len[k], len(p)-1). Used as the right part when computing cross-boundary matches for F(k+something) = F(?) + F(k). Contains only '0' and '1'.
    suffix: str                              # required, Trailing fragment of F(k) of length min(fib_len[k], len(p)-1). Used as the left part when computing cross-boundary matches for F(k+something) = F(k) + F(?). Contains only '0' and '1'.

FibStateList = list[FibState]
# Array of FibState indexed by Fibonacci level k (0..n). Used as the DP table during solve().

class InputPair:
    """A single test case consisting of Fibonacci index n and pattern p."""
    n: int                                   # required, range(0 <= value <= 100), Fibonacci word index. 0 <= n <= 100.
    pattern: str                             # required, length(1 <= len(value) <= 100000), regex(^[01]+$), Pattern to search for. 1 <= len(pattern) <= 100000. Consists only of '0' and '1'.

InputPairList = list[InputPair]
# List of all test cases parsed from stdin.

def build_failure(
    pattern: str,              # length(1 <= len(value) <= 100000), regex(^[01]+$)
) -> FailureTable:
    """
    Computes the KMP failure (prefix) function for the given pattern. The failure table is used to enable O(n+m) overlapping pattern matching. failure[0] is always 0. For each index i (1 <= i < len(pattern)), failure[i] is the length of the longest proper prefix of pattern[0..i] that is also a suffix of pattern[0..i].

    Preconditions:
      - len(pattern) >= 1
      - all characters in pattern are '0' or '1'

    Postconditions:
      - len(result) == len(pattern)
      - result[0] == 0
      - for all i in 0..len(pattern)-1: 0 <= result[i] <= i
      - for all i in 1..len(pattern)-1: result[i] is the length of the longest proper prefix of pattern[0..i] that equals pattern[0..result[i]-1] and pattern[i-result[i]+1..i]

    Errors:
      - empty_pattern (ValueError): len(pattern) == 0
          message: Pattern must be non-empty.

    Side effects: none
    Idempotent: yes
    """
    ...

def count_overlapping(
    text: str,
    pattern: str,              # length(1 <= len(value) <= 100000)
    failure: FailureTable,     # custom(len(failure) == len(pattern))
) -> int:
    """
    Counts all overlapping occurrences of pattern in text using the KMP algorithm with a precomputed failure table. After each full match, the search state resets to failure[m-1] (where m = len(pattern)) to allow overlapping matches. This function is used both for small Fibonacci words that fit in memory and for cross-boundary fragments (suffix + prefix) during the DP recurrence.

    Preconditions:
      - len(pattern) >= 1
      - len(failure) == len(pattern)
      - failure was produced by build_failure(pattern)
      - text contains only '0' and '1' (or is empty)

    Postconditions:
      - result >= 0
      - result == number of indices i in [0, len(text)-len(pattern)] such that text[i:i+len(pattern)] == pattern
      - if len(text) < len(pattern) then result == 0

    Errors:
      - empty_pattern (ValueError): len(pattern) == 0
          message: Pattern must be non-empty.
      - failure_length_mismatch (ValueError): len(failure) != len(pattern)
          message: Failure table length must match pattern length.

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    n: int,                    # range(0 <= value <= 100)
    pattern: str,              # length(1 <= len(value) <= 100000), regex(^[01]+$)
) -> int:
    """
    Main DP driver for a single test case. Given Fibonacci word index n and pattern p, computes the number of overlapping occurrences of p in F(n) without materializing F(n) for large n. Algorithm: (1) Precompute failure table via build_failure(pattern). (2) Track fib_len[k] = length of F(k), capped at a sentinel (e.g. len(pattern)+1) once it exceeds len(pattern), to avoid integer overflow in length tracking. (3) Build FibState bottom-up for k=0..n. Base cases: F(0)='0', F(1)='1'. For k>=2, F(k)=F(k-1)+F(k-2), so count(k) = count(k-1) + count(k-2) + cross_matches. cross_matches = count_overlapping(suffix[k-1]+prefix[k-2], pattern, failure) - count_overlapping(suffix[k-1], pattern, failure) - count_overlapping(prefix[k-2], pattern, failure). Prefix and suffix of F(k) are derived: prefix(k) = (prefix(k-1) + prefix(k-2))[:boundary_len] and suffix(k) = (suffix(k-1) + suffix(k-2))[-boundary_len:], where boundary_len = min(fib_len[k], len(pattern)-1). (4) Returns FibState[n].count.

    Preconditions:
      - 0 <= n <= 100
      - 1 <= len(pattern) <= 100000
      - pattern matches ^[01]+$

    Postconditions:
      - result >= 0
      - result equals the number of overlapping occurrences of pattern in F(n)
      - result can be up to 2^63 - 1 or larger (Python handles arbitrary precision)

    Errors:
      - n_out_of_range (ValueError): n < 0 or n > 100
          message: n must be between 0 and 100 inclusive.
      - empty_pattern (ValueError): len(pattern) == 0
          message: Pattern must be non-empty.
      - invalid_pattern_chars (ValueError): pattern contains characters other than '0' and '1'
          message: Pattern must consist only of '0' and '1'.

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point. Reads all input from stdin as EOF-terminated text. Parses alternating line pairs: first line is integer n, second line is pattern p. For each test case (1-indexed), calls solve(n, pattern) and prints 'Case {i}: {result}' to stdout. Each output line is terminated by a newline. Handles the case where trailing blank lines or whitespace may appear in input gracefully by stripping empty lines.

    Preconditions:
      - stdin contains zero or more test cases
      - each test case consists of two consecutive lines: an integer n on the first line and a binary pattern string on the second line
      - lines are separated by newline characters
      - input is terminated by EOF

    Postconditions:
      - for each test case i (1-indexed), exactly one line 'Case {i}: {count}' is written to stdout
      - output lines are in the same order as input test cases
      - each output line is terminated by a newline character
      - no extra output is written to stdout

    Errors:
      - odd_number_of_lines (ValueError): after stripping empty/whitespace-only lines, the number of remaining lines is odd (incomplete final test case)
          message: Input contains an incomplete test case (odd number of non-empty lines).
      - non_integer_n (ValueError): the first line of a test case cannot be parsed as a non-negative integer
          message: Expected a non-negative integer for n.
      - io_error (IOError): stdin or stdout encounters an I/O error
          message: I/O error while reading stdin or writing stdout.

    Side effects: Reads from sys.stdin, Writes to sys.stdout
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['FailureTable', 'FibState', 'FibStateList', 'InputPair', 'InputPairList', 'build_failure', 'count_overlapping', 'solve', 'main']
