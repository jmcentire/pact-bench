# === Posterize Solver (posterize_solver) v1 ===
# Implement a complete solution for the Posterize problem. Read d distinct red values with their pixel counts and parameter k from stdin. Compute the minimum sum of squared errors when choosing at most k allowed integer values from [0,255]. Uses contiguous group partitioning DP with O(1) cost lookups via prefix sums. Allowed representative values are any integer in [0,255], not restricted to input values. Single-module Python 3.10+ solution, standard library only.

# Module invariants:
#   - All functions use Python native integers; no floating-point arithmetic is used in final cost computation (weighted mean is computed as integer division for floor, +1 for ceil).
#   - The values list is always sorted in strictly increasing order of r throughout all processing.
#   - Allowed representative values range over all integers in [0, 255], not just input red values.
#   - Optimal assignment of input values to nearest representative always yields contiguous clusters in sorted order, so the contiguous partitioning DP is exact.
#   - No external dependencies; only Python 3.10+ standard library is used.
#   - Prefix sum arrays s0, s1, s2 are computed once and shared immutably across all cost() and solve() calls.
#   - The cost function evaluates at most two candidate representatives (floor and ceil of weighted mean), which is sufficient for optimality since the SSE as a function of integer v is convex.
#   - k >= d implies the answer is 0 because each distinct value can be its own representative.

class RedPixelPair:
    """A single distinct red value and its associated pixel count, as read from input."""
    r: int                                   # required, range(0 <= r <= 255), Distinct red channel value.
    p: int                                   # required, range(1 <= p <= 1000000), Number of pixels with this red value.

class ParsedInput:
    """The fully parsed input for one test case: number of distinct values d, number of allowed posterization levels k, and the sorted list of (r, p) pairs."""
    d: int                                   # required, range(1 <= d <= 256), Number of distinct red values in the input.
    k: int                                   # required, range(1 <= k <= 256), Maximum number of allowed representative integer values.
    values: RedPixelPairList                 # required, List of (r, p) pairs sorted in strictly increasing order of r. Length equals d.

RedPixelPairList = list[RedPixelPair]
# A list of RedPixelPair structs, sorted by r in strictly increasing order.

class PrefixSums:
    """Three prefix sum arrays of length d+1 enabling O(1) cost computation for any contiguous group. s0[0]=s1[0]=s2[0]=0. For index m in [1..d]: s0[m] = sum of p for values 0..m-1, s1[m] = sum of p*r for values 0..m-1, s2[m] = sum of p*r^2 for values 0..m-1."""
    s0: IntList                              # required, Prefix sums of pixel counts p. Length d+1.
    s1: IntList                              # required, Prefix sums of p*r. Length d+1.
    s2: IntList                              # required, Prefix sums of p*r^2. Length d+1.

IntList = list[int]
# A list of Python native integers.

def parse_input() -> ParsedInput:
    """
    Read all tokens from stdin and parse the single test case. First token is d (number of distinct red values), second token is k (number of allowed posterization levels). Then d lines follow, each with two integers r and p. Returns a tuple (d, k, values) where values is a list of (r, p) tuples sorted by r in strictly increasing order.

    Preconditions:
      - stdin contains exactly one well-formed test case matching the problem's input format
      - The d (r, p) pairs on stdin have strictly increasing r values

    Postconditions:
      - returned d equals the number of elements in returned values list
      - returned k is in [1, d]
      - returned values list is sorted in strictly increasing order of r
      - all r values are in [0, 255]
      - all p values are >= 1

    Errors:
      - empty_input (ValueError): stdin is empty or contains no parseable tokens
          message: No input available on stdin.
      - malformed_tokens (ValueError): Tokens cannot be converted to integers or the count of tokens does not match expected 2 + 2*d
          message: Malformed input: cannot parse expected integer tokens.
      - constraint_violation (ValueError): d < 1 or d > 256 or k < 1 or k > d or any r not in [0,255] or any p < 1
          message: Input values violate problem constraints.

    Side effects: none
    Idempotent: no
    """
    ...

def build_prefix_sums(
    values: RedPixelPairList,
) -> PrefixSums:
    """
    Given the sorted list of (r, p) pairs, compute three prefix sum arrays s0, s1, s2 each of length d+1. s0[i] = sum of p[0..i-1], s1[i] = sum of p[j]*r[j] for j in 0..i-1, s2[i] = sum of p[j]*r[j]^2 for j in 0..i-1. All arrays start with 0 at index 0.

    Preconditions:
      - values is non-empty
      - values is sorted in strictly increasing order of r
      - all r in [0, 255] and all p >= 1

    Postconditions:
      - s0, s1, s2 each have length len(values) + 1
      - s0[0] == s1[0] == s2[0] == 0
      - for all m in [1, len(values)]: s0[m] == s0[m-1] + values[m-1].p
      - for all m in [1, len(values)]: s1[m] == s1[m-1] + values[m-1].p * values[m-1].r
      - for all m in [1, len(values)]: s2[m] == s2[m-1] + values[m-1].p * values[m-1].r * values[m-1].r
      - all elements of s0, s1, s2 are non-negative integers

    Errors:
      - empty_values (ValueError): values list is empty (length 0)
          message: Cannot build prefix sums from an empty values list.

    Side effects: none
    Idempotent: yes
    """
    ...

def cost(
    i: int,                    # range(0 <= i)
    j: int,                    # range(i <= j)
    s0: IntList,
    s1: IntList,
    s2: IntList,
) -> int:
    """
    Compute the minimum weighted sum of squared errors for covering the contiguous group of distinct red values at sorted indices i..j (inclusive, 0-based) with a single representative integer in [0, 255]. The optimal representative is the weighted mean of the group's red values (weighted by pixel counts). Since the representative must be an integer, we evaluate floor(mean) and ceil(mean), clamp each to [0, 255], and return the smaller total SSE. The SSE for representative v over indices i..j is: sum_{m=i}^{j} p[m] * (r[m] - v)^2 = (s2[j+1]-s2[i]) - 2*v*(s1[j+1]-s1[i]) + v^2*(s0[j+1]-s0[i]).

    Preconditions:
      - 0 <= i <= j < len(s0) - 1
      - s0, s1, s2 are valid prefix sum arrays of equal length
      - The pixel count sum for the group (s0[j+1] - s0[i]) is > 0

    Postconditions:
      - returned value is a non-negative integer
      - returned value equals the minimum over all integer v in [0,255] of sum_{m=i}^{j} p[m]*(r[m]-v)^2
      - returned value == 0 if and only if all distinct r values in the group are the same integer

    Errors:
      - invalid_index_range (IndexError): i < 0 or j < i or j+1 >= len(s0)
          message: Index range (i, j) is out of bounds for the prefix sum arrays.
      - zero_pixel_count (ValueError): s0[j+1] - s0[i] == 0
          message: Group has zero total pixel count; weighted mean is undefined.

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    d: int,                    # range(1 <= d <= 256)
    k: int,                    # range(1 <= k <= 256)
    s0: IntList,
    s1: IntList,
    s2: IntList,
) -> int:
    """
    Compute the minimum total sum of squared errors using the contiguous group partitioning DP. dp[g][i] represents the minimum SSE achievable using exactly g representative values to cover the first i distinct red values (sorted). Base case: dp[1][i] = cost(0, i-1). Transition: dp[g][i] = min over m in [g-1, i-1] of (dp[g-1][m] + cost(m, i-1)). If k >= d, every distinct value can be its own representative, so the answer is 0. Returns dp[min(k, d)][d].

    Preconditions:
      - 1 <= d <= 256
      - 1 <= k <= 256
      - s0, s1, s2 each have length d + 1
      - s0, s1, s2 are valid prefix sum arrays produced by build_prefix_sums

    Postconditions:
      - returned value is a non-negative integer
      - returned value == 0 if k >= d
      - returned value is the global minimum SSE achievable by partitioning d sorted distinct values into at most k contiguous groups, each represented by one integer in [0, 255]

    Errors:
      - prefix_length_mismatch (ValueError): len(s0) != d + 1 or len(s1) != d + 1 or len(s2) != d + 1
          message: Prefix sum arrays must each have length d + 1.
      - invalid_d (ValueError): d < 1 or d > 256
          message: d is out of allowed range [1, 256].
      - invalid_k (ValueError): k < 1 or k > 256
          message: k is out of allowed range [1, 256].

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point and orchestrator. Calls parse_input to read the test case, build_prefix_sums to prepare O(1) cost lookups, solve to compute the DP, and prints the result as a single integer to stdout. Exactly one print() call is made.

    Preconditions:
      - stdin contains exactly one well-formed test case

    Postconditions:
      - Exactly one line is written to stdout containing the minimum SSE as a decimal integer
      - No other output is written to stdout or stderr under normal operation

    Errors:
      - input_error (ValueError): stdin is empty, malformed, or violates problem constraints (propagated from parse_input)
          message: Failed to parse valid input from stdin.

    Side effects: Reads from stdin, Writes to stdout
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['RedPixelPair', 'ParsedInput', 'RedPixelPairList', 'PrefixSums', 'IntList', 'parse_input', 'build_prefix_sums', 'cost', 'solve', 'main']
