# === Fibonacci Words Pattern Counter (fibonacci_words) v1 ===
# Counts overlapping occurrences of a bit pattern p in the Fibonacci word F(n), where F(0)='0', F(1)='1', and F(k)=F(k-1)+F(k-2) for k≥2. Uses a DP approach with KMP-based overlapping pattern matching to handle n up to 100 and patterns up to 100,000 characters. Reads test cases from stdin (pairs of lines: n then p) until EOF, outputs 'Case X: count' for each test case to stdout.

# Module invariants:
#   - F(0) is always '0' and F(1) is always '1'. F(k) = F(k-1) + F(k-2) for k >= 2 (string concatenation).
#   - All pattern matching uses overlapping semantics: for pattern 'aa' in text 'aaa', the count is 2, not 1.
#   - count_overlapping is the sole matching primitive; no other matching method (e.g., str.count, str.find loops) is used anywhere.
#   - FibState.prefix and FibState.suffix are at most len(pattern)-1 characters long, or the full Fibonacci word string if its length is less than len(pattern).
#   - FibState.length is the actual length of F(k) when F(k) is shorter than pattern, otherwise it is capped at len(pattern). This cap is sufficient for all threshold comparisons.
#   - The DP recurrence is: count(k) = count(k-1) + count(k-2) + cross(k), where cross(k) = count_overlapping(suffix(k-1) + prefix(k-2), pattern) - count_overlapping(suffix(k-1), pattern) - count_overlapping(prefix(k-2), pattern).
#   - No global mutable state exists. All state is passed through function arguments and return values.
#   - I/O is isolated exclusively in the main() function. All other functions are pure.
#   - Only Python 3.10+ standard library modules are used. No external dependencies.
#   - Output format is exactly 'Case X: count' with a trailing newline for each test case, where X is 1-based.

class FibState:
    """Immutable per-level DP record for a single Fibonacci word F(k). Tracks the overlapping occurrence count of the pattern within F(k), the prefix and suffix strings of F(k) (each at most len(pattern)-1 characters, or the full string if F(k) is shorter than the pattern), and the actual length of F(k) (capped at a sentinel value once it exceeds len(pattern) to simplify comparisons)."""
    count: int                               # required, range(count >= 0), Number of overlapping occurrences of the pattern in F(k). Non-negative. Can grow up to 2^63-1 or beyond; Python arbitrary-precision ints handle this.
    prefix: str                              # required, regex(^[01]*$), The first min(len(F(k)), len(pattern)-1) characters of F(k). Contains only '0' and '1'. Used to compute cross-boundary matches when F(k) appears as the right part of a concatenation.
    suffix: str                              # required, regex(^[01]*$), The last min(len(F(k)), len(pattern)-1) characters of F(k). Contains only '0' and '1'. Used to compute cross-boundary matches when F(k) appears as the left part of a concatenation.
    length: int                              # required, range(length >= 1), Actual length of F(k), but capped at len(pattern) once it reaches or exceeds len(pattern). This cap avoids tracking astronomically large Fibonacci word lengths while still allowing the small-vs-large threshold check (length < len(pattern)).

class TestCase:
    """A single parsed test case consisting of the Fibonacci word index n and the bit pattern p to search for."""
    n: int                                   # required, range(0 <= n <= 100), Index of the Fibonacci word F(n) to search within.
    pattern: str                             # required, regex(^[01]+$), length(1 <= len(pattern) <= 100000), The bit pattern to count overlapping occurrences of within F(n).

KMPFailureTable = list[int]
# The KMP failure function (partial match table) for a pattern. A list of ints of the same length as the pattern, where entry i is the length of the longest proper prefix of pattern[0..i] that is also a suffix. Used internally by count_overlapping.

def build_kmp_failure_table(
    pattern: str,              # length(len(pattern) >= 1), regex(^[01]+$)
) -> KMPFailureTable:
    """
    Builds the KMP failure (partial match) table for the given pattern. The failure table is used by count_overlapping to efficiently find all overlapping occurrences. Entry i holds the length of the longest proper prefix of pattern[0..i] that is also a suffix of pattern[0..i].

    Preconditions:
      - pattern is a non-empty string of '0' and '1' characters.

    Postconditions:
      - Returned list has the same length as pattern.
      - failure_table[0] == 0.
      - For all i in 0..len(pattern)-1: 0 <= failure_table[i] <= i.
      - For all i: pattern[0:failure_table[i]] == pattern[i-failure_table[i]+1:i+1].

    Errors:
      - empty_pattern (ValueError): len(pattern) == 0
          message: Pattern must be non-empty for KMP failure table construction.

    Side effects: none
    Idempotent: yes
    """
    ...

def count_overlapping(
    text: str,                 # regex(^[01]*$)
    pattern: str,              # length(len(pattern) >= 1), regex(^[01]+$)
) -> int:
    """
    Counts the number of overlapping occurrences of pattern in text using the KMP algorithm. This is the sole matching primitive — all pattern matching in the solution goes through this function. Unlike str.count, this correctly finds overlapping matches (e.g., counting 'aa' in 'aaa' returns 2).

    Preconditions:
      - pattern is a non-empty string of '0' and '1'.
      - text is a (possibly empty) string of '0' and '1'.

    Postconditions:
      - Returned value is >= 0.
      - Returned value equals the number of indices i in range(len(text) - len(pattern) + 1) where text[i:i+len(pattern)] == pattern.
      - If len(text) < len(pattern), returned value is 0.

    Errors:
      - empty_pattern (ValueError): len(pattern) == 0
          message: Pattern must be non-empty.

    Side effects: none
    Idempotent: yes
    """
    ...

def make_base_fib_state(
    base_string: str,          # regex(^[01]$)
    pattern: str,              # length(len(pattern) >= 1), regex(^[01]+$)
) -> FibState:
    """
    Constructs the FibState for a base-case Fibonacci word (F(0)='0' or F(1)='1') given the pattern. Counts overlapping occurrences of pattern in the single-character string, and sets prefix, suffix, and length accordingly. Since F(0) and F(1) are single characters, the prefix and suffix are that character (unless len(pattern)-1 is 0, i.e., pattern has length 1, in which case prefix/suffix are truncated to length 0, but the full string is still used for the small-string path).

    Preconditions:
      - base_string is '0' or '1'.
      - pattern is a non-empty string of '0' and '1'.

    Postconditions:
      - Returned FibState.length == 1.
      - Returned FibState.count == (1 if base_string == pattern else 0).
      - len(Returned FibState.prefix) == min(1, len(pattern) - 1).
      - len(Returned FibState.suffix) == min(1, len(pattern) - 1).

    Side effects: none
    Idempotent: yes
    """
    ...

def combine_fib_states(
    left: FibState,
    right: FibState,
    pattern: str,              # length(len(pattern) >= 1), regex(^[01]+$)
) -> FibState:
    """
    Combines two FibState values representing F(k-1) (left) and F(k-2) (right) to produce the FibState for F(k) = F(k-1) + F(k-2). Computes cross-boundary matches by forming the junction string (suffix of left + prefix of right), counting overlapping pattern matches in the junction, and subtracting matches fully within the suffix and prefix pieces. Updates prefix, suffix, and length for the combined Fibonacci word. Handles the 'small' case where the combined length is still less than len(pattern) by concatenating prefix and suffix to form the full string.

    Preconditions:
      - left and right are valid FibState instances with consistent prefix/suffix/length values.
      - pattern is a non-empty string of '0' and '1'.
      - left.prefix and left.suffix have length min(left.length, len(pattern)-1).
      - right.prefix and right.suffix have length min(right.length, len(pattern)-1).

    Postconditions:
      - Returned FibState.count == left.count + right.count + cross_boundary_matches.
      - cross_boundary_matches == count_overlapping(left.suffix + right.prefix, pattern) - count_overlapping(left.suffix, pattern) - count_overlapping(right.prefix, pattern).
      - Returned FibState.length == min(left.length + right.length, len(pattern)) if either was already capped, else left.length + right.length capped at len(pattern).
      - len(Returned FibState.prefix) == min(Returned FibState.length, len(pattern) - 1).
      - len(Returned FibState.suffix) == min(Returned FibState.length, len(pattern) - 1).
      - Returned FibState.count >= 0.

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    n: int,                    # range(0 <= n <= 100)
    pattern: str,              # length(1 <= len(pattern) <= 100000), regex(^[01]+$)
) -> int:
    """
    Core DP solver. Given a Fibonacci word index n and a bit pattern, computes the number of overlapping occurrences of the pattern in F(n). Builds base cases for F(0) and F(1), then iterates from k=2 to k=n, combining FibState values at each step using combine_fib_states. Returns the final count. Handles edge cases: if n is 0 or 1, returns the base case count directly.

    Preconditions:
      - 0 <= n <= 100.
      - pattern is a non-empty string of '0' and '1' with length <= 100,000.

    Postconditions:
      - Returned value >= 0.
      - Returned value equals the exact number of overlapping occurrences of pattern in the Fibonacci word F(n).
      - For n=0: returned value == count_overlapping('0', pattern).
      - For n=1: returned value == count_overlapping('1', pattern).

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

def parse_input(
    raw_input: str,
) -> list:
    """
    Reads all input from stdin and parses it into a list of TestCase values. Input format: pairs of lines until EOF, where the first line of each pair is n (integer) and the second line is the bit pattern p. Strips whitespace from each line. Stops at EOF.

    Preconditions:
      - raw_input contains an even number of non-empty lines (pairs of n and pattern).
      - Each n line is a valid integer string in range [0, 100].
      - Each pattern line is a non-empty string of '0' and '1' characters with length <= 100,000.

    Postconditions:
      - Returned list contains one TestCase per pair of input lines.
      - TestCases are in the same order as they appear in the input.
      - Each TestCase.n is the parsed integer from the first line of the pair.
      - Each TestCase.pattern is the stripped string from the second line of the pair.

    Errors:
      - odd_number_of_lines (ValueError): The number of non-empty lines in raw_input is odd
          message: Input must contain an even number of non-empty lines (pairs of n and pattern).
      - invalid_n_value (ValueError): A line expected to be n cannot be parsed as an integer or is out of range [0, 100]
          message: Invalid value for n: must be an integer in [0, 100].
      - invalid_pattern_value (ValueError): A pattern line is empty or contains characters other than '0' and '1'
          message: Invalid pattern: must be a non-empty string of '0' and '1'.

    Side effects: none
    Idempotent: yes
    """
    ...

def format_output(
    case_number: int,          # range(case_number >= 1)
    count: int,                # range(count >= 0)
) -> str:
    """
    Formats a single test case result as the required output line: 'Case X: count' where X is the 1-based case number and count is the occurrence count.

    Preconditions:
      - case_number >= 1.
      - count >= 0.

    Postconditions:
      - Returned string matches the regex '^Case \d+: \d+$'.
      - The case number in the output equals case_number.
      - The count in the output equals count.

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point. Reads all input from stdin, parses test cases, solves each one by calling solve, and prints 'Case X: count' for each test case (1-based indexing) to stdout. Each output line is terminated with a newline. This is the only function that performs I/O.

    Preconditions:
      - stdin contains valid input: pairs of lines (n, pattern) until EOF.
      - Each n is an integer in [0, 100].
      - Each pattern is a non-empty string of '0'/'1' with length <= 100,000.

    Postconditions:
      - Stdout contains one line per test case in the format 'Case X: count' with 1-based indexing.
      - Lines are separated by newlines.
      - Output exactly matches expected format with no trailing spaces on any line.
      - All test cases are processed in input order.

    Errors:
      - eof_read_error (IOError): stdin cannot be read or is unavailable
          message: Failed to read from stdin.
      - malformed_input (ValueError): Input does not conform to expected format (pairs of lines with valid n and pattern)
          message: Malformed input: expected pairs of lines with integer n and bit pattern p.

    Side effects: Reads from stdin., Writes to stdout.
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['FibState', 'TestCase', 'KMPFailureTable', 'build_kmp_failure_table', 'count_overlapping', 'make_base_fib_state', 'combine_fib_states', 'solve', 'parse_input', 'format_output', 'main']
