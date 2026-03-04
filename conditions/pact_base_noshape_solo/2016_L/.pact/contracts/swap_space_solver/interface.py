# === Swap Space Solver (swap_space_solver) v1 ===
# Implement a solution for the Swap Space problem. The program reads n drives with old capacity a and new capacity b from stdin, and determines the minimum extra storage needed to reformat all drives. Uses a greedy ordering strategy: gainers (b >= a) sorted by a ascending, then losers (b < a) sorted by b descending. Computes the answer via direct single-pass simulation in O(n log n) time (dominated by sorting). Reads from stdin, writes to stdout. Python 3.10+ standard library only (sys).

# Module invariants:
#   - The program uses only Python 3.10+ standard library (sys module for I/O).
#   - No external packages or dependencies are imported.
#   - The greedy processing order is always: gainers (b >= a) sorted by a ascending, then losers (b < a) sorted by b descending.
#   - The solve function is pure: given the same input list, it always returns the same result.
#   - The output is always a single non-negative integer on one line.
#   - For any valid input, the algorithm terminates in O(n log n) time and O(n) auxiliary space.
#   - The minimum extra space S satisfies: simulating the reformat in greedy order starting with free_space = S, free_space never drops below 0.
#   - S is minimal: for any S' < S, the simulation would produce a negative free_space at some step.

class Drive:
    """A single drive with its old capacity and new capacity after reformatting."""
    a: int                                   # required, range(a >= 0), Old capacity of the drive (before reformatting). Non-negative integer.
    b: int                                   # required, range(b >= 0), New capacity of the drive (after reformatting). Non-negative integer.

DriveList = list[Drive]
# A list of Drive tuples represented as list[tuple[int, int]]. Each element is a (a, b) pair.

ExtraSpace = primitive  # The minimum extra storage space required, represented as a non-negative int.

def parse_input() -> DriveList:
    """
    Reads all input from sys.stdin at once using sys.stdin.read().split() for performance. Parses the first token as n (number of drives), then reads n pairs of integers (a_i, b_i). Returns a list of (a, b) tuples. The length of the returned list equals n. Does not return n separately since len(drives) suffices.

    Preconditions:
      - sys.stdin contains well-formed input: first line is integer n >= 0, followed by n lines each containing two space-separated non-negative integers a and b.
      - All integer values fit within Python's arbitrary-precision int (no overflow concern).
      - 0 <= n <= 1000000.

    Postconditions:
      - Returned list has exactly n elements, where n is the first integer read from stdin.
      - Each element (a, b) faithfully represents one input line with a >= 0 and b >= 0.
      - Input is fully consumed from stdin after this call.

    Errors:
      - empty_stdin (ValueError): sys.stdin is empty or contains no tokens.
          message: No input available on stdin.
      - malformed_n (ValueError): The first token cannot be parsed as a non-negative integer.
          message: First token is not a valid non-negative integer for n.
      - insufficient_tokens (ValueError): Fewer than 2*n additional tokens are available after reading n.
          message: Input contains fewer drive entries than specified by n.
      - non_integer_token (ValueError): A token in the drive data cannot be parsed as a non-negative integer.
          message: Drive capacity token is not a valid non-negative integer.

    Side effects: Reads from sys.stdin (consumed entirely).
    Idempotent: no
    """
    ...

def solve(
    drives: DriveList,         # custom(all(a >= 0 and b >= 0 for a, b in drives))
) -> ExtraSpace:
    """
    Pure function. Computes the minimum extra storage space S needed to reformat all drives. Algorithm: (1) Partition drives into gainers (b >= a) and losers (b < a). (2) Sort gainers by a ascending (reformat cheapest first to free space quickly). (3) Sort losers by b descending (reformat those losing least new capacity first to preserve free space). (4) Concatenate: gainers first, then losers. (5) Single-pass simulation: maintain prefix_net = running sum of (b_k - a_k) for processed drives. Before processing drive i, the free space is S + prefix_net_{i-1}. We need S + prefix_net_{i-1} >= a_i, i.e., S >= a_i - prefix_net_{i-1}. So S = max(0, max over all i of (a_i - prefix_net_{i-1})). Computed in O(n) after O(n log n) sorting.

    Preconditions:
      - drives is a list of (a, b) tuples with a >= 0 and b >= 0 for all entries.
      - len(drives) <= 1000000.

    Postconditions:
      - Returned value S is a non-negative integer (S >= 0).
      - S is the minimum extra storage such that all drives can be reformatted in the greedy order without available space going negative.
      - If drives is empty, S == 0.
      - If all drives have a == 0, S == 0 (no space needed to move zero data).
      - For a single drive (a, b), S == a (must have enough to hold all data from that one drive).
      - S <= sum of all a values in drives (upper bound: enough to hold all data simultaneously).

    Errors:
      - negative_capacity (ValueError): Any drive has a < 0 or b < 0.
          message: Drive capacities must be non-negative.

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point. Calls parse_input() to read drive data from stdin, passes the result to solve() to compute the minimum extra space, then prints the integer result to stdout followed by a newline. This is the function invoked when the script is run directly.

    Preconditions:
      - sys.stdin contains valid input as specified by the problem statement.
      - stdout is writable.

    Postconditions:
      - Exactly one line is written to stdout containing the minimum extra space as a non-negative integer.
      - Output is followed by a newline character.
      - No other output is written to stdout or stderr during normal execution.

    Errors:
      - input_error (ValueError): parse_input() raises ValueError due to malformed input.
          message: Input parsing failed; see parse_input error cases.
      - io_error (IOError): Reading stdin or writing stdout fails due to I/O error.
          message: I/O operation on stdin or stdout failed.

    Side effects: Reads from sys.stdin via parse_input()., Writes result to sys.stdout via print().
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['Drive', 'DriveList', 'parse_input', 'solve', 'main']
