# === Swap Space Solution (solution) v1 ===
# Implement solution.py that solves the Swap Space problem. Given n drives with old capacities a_i and new capacities b_i, determine the minimum extra storage E needed to reformat all drives. Uses a greedy ordering strategy: reformat growing drives first (sorted by a_i ascending), then shrinking drives (sorted by b_i descending). Simulates free space tracking to compute the answer directly without binary search. Reads from stdin, writes to stdout. O(n log n) time, O(n) space, standard library only.

# Module invariants:
#   - The program uses only the Python 3.10+ standard library; no external dependencies.
#   - All functions have complete type annotations.
#   - The greedy ordering is: growers (b >= a) sorted by a ascending, then shrinkers (b < a) sorted by b descending.
#   - The simulation computes the minimum extra space E by tracking the minimum free space encountered: E = max(0, -min_free) where min_free is the running minimum of cumulative (sum of b_i - a_i) over the prefix.
#   - The answer E is always >= 0.
#   - For n >= 1 with all capacities >= 1, the answer E >= min(a_i) of the first drive in the sorted order (since the first drive must be fully evacuated with no prior free space from other drives).
#   - Time complexity is O(n log n) dominated by sorting; space complexity is O(n).
#   - Output is exactly one line containing the integer E with no leading zeros (except E=0 itself), no trailing spaces, terminated by a newline.
#   - The file contains an if __name__ == '__main__': main() guard.

class Drive:
    """A single drive with its old (pre-reformat) capacity and new (post-reformat) capacity."""
    old_capacity: int                        # required, range(1 <= old_capacity <= 1000000000), The current capacity a_i of the drive before reformatting. Represents the amount of data that must be evacuated.
    new_capacity: int                        # required, range(1 <= new_capacity <= 1000000000), The capacity b_i of the drive after reformatting. Represents the free space gained after reformatting.

DriveList = list[Drive]
# A list of Drive structs representing all drives to be reformatted.

class RawInput:
    """Parsed representation of the full problem input from stdin."""
    n: int                                   # required, range(1 <= n <= 1000000), Number of drives.
    drives: DriveList                        # required, The list of n drives parsed from input.

def parse_input(
    raw_text: str,
) -> RawInput:
    """
    Read all input from stdin via sys.stdin.read(), split into tokens, and parse into a RawInput structure. The input format is: first line contains integer n, followed by n lines each containing two integers a_i and b_i.

    Preconditions:
      - raw_text is non-empty and contains at least one integer token.
      - raw_text contains exactly 1 + 2*n whitespace-separated integer tokens where n is the first token.

    Postconditions:
      - Returned RawInput.n equals the number of drives in RawInput.drives.
      - All Drive.old_capacity and Drive.new_capacity values are in range [1, 10^9].
      - RawInput.n is in range [1, 10^6].

    Errors:
      - empty_input (ValueError): raw_text is empty or contains only whitespace.
          message: Input is empty.
      - insufficient_tokens (ValueError): raw_text does not contain enough tokens (expected 1 + 2*n tokens).
          message: Input does not contain the expected number of tokens.
      - non_integer_token (ValueError): A token cannot be parsed as an integer.
          message: Input contains a non-integer token.
      - n_out_of_range (ValueError): Parsed n is less than 1 or greater than 10^6.
          message: n is out of valid range [1, 10^6].
      - capacity_out_of_range (ValueError): Any a_i or b_i is less than 1 or greater than 10^9.
          message: Drive capacity is out of valid range [1, 10^9].

    Side effects: none
    Idempotent: yes
    """
    ...

def solve(
    drives: DriveList,
) -> int:
    """
    Given a list of drives, compute the minimum extra storage E needed to reformat all drives. Strategy: split drives into growers (new_capacity >= old_capacity) and shrinkers (new_capacity < old_capacity). Sort growers by old_capacity ascending, shrinkers by new_capacity descending. Concatenate growers then shrinkers. Simulate free space: start free=0, min_free=0. For each drive: free -= old_capacity; min_free = min(min_free, free); free += new_capacity. Return max(0, -min_free).

    Preconditions:
      - drives is non-empty (len(drives) >= 1).
      - All drives have old_capacity >= 1 and new_capacity >= 1.

    Postconditions:
      - Returned value E >= 0.
      - E is the minimum extra storage such that all drives can be reformatted in the computed optimal order without free space ever going negative.
      - Starting with free_space = E and processing drives in the optimal greedy order, free_space >= 0 at every step (after evacuating each drive).
      - No smaller non-negative integer E' < E satisfies the above property for any ordering of drives.

    Errors:
      - empty_drive_list (ValueError): drives list is empty (length 0).
          message: Drive list must be non-empty.

    Side effects: none
    Idempotent: yes
    """
    ...

def main() -> None:
    """
    Entry point. Reads all input from stdin via sys.stdin.read(), parses it with parse_input, computes the answer with solve, and prints the single integer result to stdout followed by a newline.

    Preconditions:
      - stdin contains valid input conforming to the problem format.
      - Program is invoked as the main module.

    Postconditions:
      - Exactly one line is written to stdout containing the integer result.
      - The printed integer is the minimum extra storage E needed to reformat all drives.
      - No other output is written to stdout or stderr.

    Errors:
      - stdin_read_failure (IOError): sys.stdin.read() raises an I/O error.
          message: Failed to read from stdin.
      - invalid_input_format (ValueError): Input from stdin does not conform to expected format, propagated from parse_input.
          message: Invalid input format.

    Side effects: Reads from stdin (consumes entire stdin stream)., Writes result to stdout.
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['Drive', 'DriveList', 'RawInput', 'parse_input', 'solve', 'main']
