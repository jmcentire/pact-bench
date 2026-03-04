# === Posterize Solution (posterize_solution) v1 ===
# Implement a complete solution for the Posterize problem. The solution reads d distinct red values with their pixel counts and a parameter k, then computes the minimum sum of squared errors when replacing all red intensities with at most k allowed integer values from [0, 255]. Uses integer arithmetic throughout, prefix sums for O(1) interval cost computation, and a 2D DP over k partitions of d sorted values. Single-file Python 3.10+ module reading from stdin and writing to stdout.

# Module invariants:
#   - All arithmetic for SSE computation uses Python integers; no floating-point arithmetic is used except for the float('inf') sentinel in DP initialization
#   - Allowed replacement values are any integer in [0, 255], not restricted to input red values
#   - The values array is always sorted in strictly ascending order throughout all computations
#   - Prefix sum arrays are immutable after construction and have length exactly d + 1
#   - dp[m][0] == 0 for all m in [1, k]: zero distinct values require zero error
#   - dp[1][i] == compute_cost(0, i-1) for all i in [1, d]: base case uses single representative for first i values
#   - dp[m][i] <= dp[m-1][i] for all valid m, i: more allowed values never increases the minimum SSE
#   - The final answer dp[k][d] is a non-negative integer
#   - For k >= d, the answer is always 0 (each distinct value maps to itself)
#   - The compute_cost function for a single element (a == b) returns 0 when the element's value is in [0, 255] (the representative equals the value itself)
#   - SSE formula for representative v: sum_r2p - 2*v*sum_rp + v^2*sum_p, where sums are over the interval [a, b]

int = primitive  # Python integer, arbitrary precision. Used for all arithmetic to avoid floating-point issues.

float = primitive  # Python float. Used only as float('inf') sentinel in DP initialization.

str = primitive  # Python string type.

bool = primitive  # Python boolean type.

None = primitive  # Python None type.

IntList = list[int]
# A list of integers. Used for values, counts, and prefix sum arrays.

DPCell = int | float

DPRow = list[DPCell]
# A single row of the DP table, indexed by number of distinct values covered (0..d).

DPTable = list[DPRow]
# The full DP table: dp[m][i] = minimum SSE using m allowed values for the first i distinct red values. Indexed m in 0..k, i in 0..d.

class PrefixSums:
    """Three prefix sum arrays of length d+1 enabling O(1) interval queries for cost computation."""
    prefix_p: IntList                        # required, Prefix sums of pixel counts. prefix_p[i] = sum(counts[0..i-1]). prefix_p[0] = 0.
    prefix_rp: IntList                       # required, Prefix sums of (red_value * pixel_count). prefix_rp[i] = sum(values[j]*counts[j] for j in 0..i-1). prefix_rp[0] = 0.
    prefix_r2p: IntList                      # required, Prefix sums of (red_value^2 * pixel_count). prefix_r2p[i] = sum(values[j]^2*counts[j] for j in 0..i-1). prefix_r2p[0] = 0.

class ParsedInput:
    """The fully parsed input for the Posterize problem."""
    d: int                                   # required, Number of distinct red values present in the image.
    k: int                                   # required, Maximum number of allowed integer values in [0, 255] to use as replacements.
    values: IntList                          # required, Sorted list of d distinct red values, each in [0, 255].
    counts: IntList                          # required, List of d pixel counts corresponding to each red value. Each count >= 1.

def main() -> None:
    """
    Entry point. Reads the entire input from stdin, parses it, calls solve(), and prints the result as a single integer to stdout. Invoked when the module is run as __main__.

    Preconditions:
      - stdin contains well-formed input: first line is 'd k', followed by d lines each containing 'red_value pixel_count', sorted by red_value ascending
      - 1 <= d <= 256
      - 1 <= k <= d
      - All red values are distinct integers in [0, 255]
      - All pixel counts are positive integers

    Postconditions:
      - Exactly one line is written to stdout containing the minimum SSE as a non-negative integer
      - No trailing spaces; single trailing newline from print()

    Errors:
      - empty_input (IndexError): stdin is empty or contains no tokens
          detail: Insufficient tokens when parsing input
      - malformed_input (ValueError): Tokens cannot be parsed as integers
          detail: Non-integer token encountered during parsing

    Side effects: Reads from stdin via sys.stdin.read(), Writes result to stdout via print()
    Idempotent: yes
    """
    ...

def solve(
    d: int,                    # range(1 <= d <= 256)
    k: int,                    # range(1 <= k <= 256)
    values: IntList,           # length(len(values) == d), custom(all(0 <= v <= 255 for v in values)), custom(values == sorted(set(values)))
    counts: IntList,           # length(len(counts) == d), custom(all(c >= 1 for c in counts))
) -> int:
    """
    Core algorithm. Given d distinct red values (sorted ascending) with their pixel counts and parameter k, computes the minimum sum of squared errors when replacing all red intensities with at most k allowed integer values from [0, 255]. Returns 0 immediately if k >= d. Otherwise builds prefix sum arrays, defines compute_cost for O(1) interval SSE, and runs 2D DP: dp[m][i] = min SSE using m allowed values for the first i distinct red values.

    Preconditions:
      - values is sorted in strictly ascending order
      - len(values) == len(counts) == d
      - All values in [0, 255], all counts >= 1
      - 1 <= k <= 256, 1 <= d <= 256

    Postconditions:
      - Return value >= 0
      - If k >= d, return value == 0
      - Return value equals the minimum possible sum of squared errors over all choices of at most k allowed integer values from [0, 255]
      - Return value is an exact integer (no floating-point approximation)

    Errors:
      - empty_values (ValueError): d > 0 but values or counts is empty
          detail: values and counts must each have length d
      - mismatched_lengths (ValueError): len(values) != d or len(counts) != d
          detail: Length of values and counts must match d

    Side effects: none
    Idempotent: yes
    """
    ...

def build_prefix_sums(
    d: int,                    # range(d >= 1)
    values: IntList,
    counts: IntList,
) -> PrefixSums:
    """
    Constructs three prefix sum arrays from the sorted values and counts arrays. prefix_p[i] = sum(counts[0..i-1]), prefix_rp[i] = sum(values[j]*counts[j] for j in 0..i-1), prefix_r2p[i] = sum(values[j]^2*counts[j] for j in 0..i-1). All arrays have length d+1 with index 0 being 0.

    Preconditions:
      - len(values) == len(counts) == d
      - d >= 1

    Postconditions:
      - All three arrays in the result have length d + 1
      - All three arrays have index 0 equal to 0
      - prefix_p[i] = prefix_p[i-1] + counts[i-1] for 1 <= i <= d
      - prefix_rp[i] = prefix_rp[i-1] + values[i-1] * counts[i-1] for 1 <= i <= d
      - prefix_r2p[i] = prefix_r2p[i-1] + values[i-1]^2 * counts[i-1] for 1 <= i <= d

    Side effects: none
    Idempotent: yes
    """
    ...

def compute_cost(
    a: int,                    # range(0 <= a)
    b: int,                    # range(b < d), custom(a <= b)
    prefix_p: IntList,
    prefix_rp: IntList,
    prefix_r2p: IntList,
) -> int:
    """
    Computes the minimum SSE for a contiguous interval of sorted distinct red values [a, b] (inclusive indices into the values array) when all pixels in that interval are represented by a single optimal integer in [0, 255]. Uses prefix sum arrays for O(1) computation. The optimal representative is found by computing the weighted mean S/P (where S = sum of r_i*p_i, P = sum of p_i over the interval), trying floor(S/P) and ceil(S/P) clamped to [0, 255], and returning the SSE for whichever is lower. SSE for representative v = sum_r2p - 2*v*sum_rp + v^2*sum_p.

    Preconditions:
      - 0 <= a <= b < d
      - All prefix arrays have length d + 1
      - Prefix arrays are consistent with the underlying values and counts

    Postconditions:
      - Return value >= 0
      - Return value equals min over v in [0,255] of sum(counts[i] * (values[i] - v)^2 for i in a..b)
      - Only floor(S/P) and ceil(S/P) are evaluated as candidate representatives (these are provably optimal among integers)
      - Return value is computed using integer arithmetic only

    Errors:
      - invalid_interval (IndexError): a > b or b >= d
          detail: Interval indices out of bounds or inverted
      - zero_total_count (ZeroDivisionError): sum_p for interval [a, b] is zero (should not occur given valid input)
          detail: Total pixel count in interval is zero, cannot compute weighted mean

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['IntList', 'DPCell', 'DPRow', 'DPTable', 'PrefixSums', 'ParsedInput', 'main', 'solve', 'build_prefix_sums', 'compute_cost', 'ZeroDivisionError']
