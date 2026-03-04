"""
Contract test suite for the swap space solution.

Tests are organized in three sections:
1. parse_input tests — error conditions and valid boundary inputs
2. solve tests — scenario categories, brute-force verification, invariants
3. main integration tests — stdin/stdout mocking
"""

import pytest
import sys
import io
import re
import random
import itertools
from unittest.mock import patch, MagicMock

# Import the component under test
from src.solution import parse_input, solve, main

# Try to import the struct types; they may be named differently
try:
    from src.solution import Drive, RawInput
except ImportError:
    # If not directly importable, we'll work with whatever parse_input returns
    Drive = None
    RawInput = None


# ---------------------------------------------------------------------------
# Helper: simulation oracle
# ---------------------------------------------------------------------------

def simulate_swap(extra: int, ordered_drives) -> bool:
    """
    Given extra swap space E and a list of (old_capacity, new_capacity) tuples
    in a specific processing order, return True if free space never goes
    negative after evacuating each drive.
    """
    free = extra
    for old_cap, new_cap in ordered_drives:
        free -= old_cap
        if free < 0:
            return False
        free += new_cap
    return True


def brute_force_min_swap(drives_tuples):
    """
    Try all permutations of drives and find the minimum extra swap E.
    Each drive is (old_capacity, new_capacity).
    Returns the minimum E >= 0 such that some permutation succeeds.
    """
    min_e = float('inf')
    for perm in itertools.permutations(drives_tuples):
        # Binary-search or compute analytically for this permutation
        free = 0
        min_free = 0
        for old_cap, new_cap in perm:
            free -= old_cap
            if free < min_free:
                min_free = free
            free += new_cap
        e = max(0, -min_free)
        if e < min_e:
            min_e = e
    return min_e


def make_drive(old_cap, new_cap):
    """Create a Drive struct. Tries the Drive constructor, falls back to a namedtuple-like approach."""
    if Drive is not None:
        return Drive(old_capacity=old_cap, new_capacity=new_cap)
    else:
        # Fallback: create a simple object
        class _Drive:
            def __init__(self, old_capacity, new_capacity):
                self.old_capacity = old_capacity
                self.new_capacity = new_capacity
        return _Drive(old_capacity=old_cap, new_capacity=new_cap)


def make_drive_list(tuples):
    """Create a list of Drive structs from a list of (old, new) tuples."""
    return [make_drive(o, n) for o, n in tuples]


def greedy_order(drives_tuples):
    """
    Compute the greedy ordering: growers (b >= a) sorted by a ascending,
    then shrinkers (b < a) sorted by b descending.
    Returns the ordered list of (old_capacity, new_capacity) tuples.
    """
    growers = [(a, b) for a, b in drives_tuples if b >= a]
    shrinkers = [(a, b) for a, b in drives_tuples if b < a]
    growers.sort(key=lambda x: x[0])
    shrinkers.sort(key=lambda x: x[1], reverse=True)
    return growers + shrinkers


# ===========================================================================
# SECTION 1: parse_input tests
# ===========================================================================

class TestParseInputHappyPath:
    """Valid input parsing tests."""

    def test_parse_input_valid_single_drive(self):
        """Parse valid input with a single drive (N=1)."""
        result = parse_input("1\n5 10\n")
        assert result.n == 1, f"Expected n=1, got {result.n}"
        assert len(result.drives) == 1, f"Expected 1 drive, got {len(result.drives)}"
        assert result.drives[0].old_capacity == 5, f"Expected old_capacity=5, got {result.drives[0].old_capacity}"
        assert result.drives[0].new_capacity == 10, f"Expected new_capacity=10, got {result.drives[0].new_capacity}"

    def test_parse_input_valid_typical(self):
        """Parse valid input with typical N=3 drives."""
        result = parse_input("3\n1 2\n3 4\n5 6\n")
        assert result.n == 3, f"Expected n=3, got {result.n}"
        assert len(result.drives) == 3, f"Expected 3 drives, got {len(result.drives)}"
        assert result.drives[0].old_capacity == 1
        assert result.drives[0].new_capacity == 2
        assert result.drives[1].old_capacity == 3
        assert result.drives[1].new_capacity == 4
        assert result.drives[2].old_capacity == 5
        assert result.drives[2].new_capacity == 6

    def test_parse_input_valid_boundary_capacities(self):
        """Parse input with boundary capacity values (1 and 10^9)."""
        result = parse_input("2\n1 1000000000\n1000000000 1\n")
        assert result.n == 2
        assert result.drives[0].old_capacity == 1
        assert result.drives[0].new_capacity == 1000000000
        assert result.drives[1].old_capacity == 1000000000
        assert result.drives[1].new_capacity == 1

    def test_parse_input_n_equals_one_is_min(self):
        """Parse input with N=1 (minimum valid N)."""
        result = parse_input("1\n1 1\n")
        assert result.n == 1
        assert len(result.drives) == 1
        assert result.drives[0].old_capacity == 1
        assert result.drives[0].new_capacity == 1

    def test_parse_input_whitespace_variations(self):
        """Parse input with extra whitespace between tokens (should still work)."""
        result = parse_input("2  \n  1   2  \n  3   4  \n")
        assert result.n == 2
        assert len(result.drives) == 2

    def test_parse_input_postcondition_n_equals_drives_length(self):
        """Postcondition: RawInput.n equals the number of drives."""
        for n in [1, 2, 5]:
            lines = [str(n)]
            for i in range(n):
                lines.append(f"{i + 1} {i + 10}")
            raw_text = "\n".join(lines) + "\n"
            result = parse_input(raw_text)
            assert result.n == len(result.drives), (
                f"n={result.n} but len(drives)={len(result.drives)}"
            )

    def test_parse_input_all_capacities_in_range(self):
        """Postcondition: All capacities are in [1, 10^9]."""
        result = parse_input("3\n1 1000000000\n500 999999999\n1000000000 1\n")
        for drive in result.drives:
            assert 1 <= drive.old_capacity <= 10**9, f"old_capacity {drive.old_capacity} out of range"
            assert 1 <= drive.new_capacity <= 10**9, f"new_capacity {drive.new_capacity} out of range"


class TestParseInputErrors:
    """Error condition tests for parse_input."""

    def test_parse_input_error_empty_input(self):
        """Raise error when raw_text is empty."""
        with pytest.raises(Exception) as exc_info:
            parse_input("")
        # The error type/message should indicate empty input

    def test_parse_input_error_whitespace_only(self):
        """Raise error when raw_text contains only whitespace."""
        with pytest.raises(Exception) as exc_info:
            parse_input("   \n  \n")

    def test_parse_input_error_insufficient_tokens(self):
        """Raise error when tokens are fewer than 1 + 2*n."""
        with pytest.raises(Exception) as exc_info:
            parse_input("3\n1 2\n3 4\n")
        # Should indicate insufficient tokens (expected 7 tokens, got 5)

    def test_parse_input_error_insufficient_tokens_only_n(self):
        """Raise error when only n is provided with no drive data."""
        with pytest.raises(Exception) as exc_info:
            parse_input("5\n")

    def test_parse_input_error_non_integer_token(self):
        """Raise error when a token cannot be parsed as integer."""
        with pytest.raises(Exception) as exc_info:
            parse_input("2\n1 abc\n3 4\n")

    def test_parse_input_error_non_integer_n(self):
        """Raise error when n itself is not an integer."""
        with pytest.raises(Exception) as exc_info:
            parse_input("xyz\n1 2\n")

    def test_parse_input_error_n_out_of_range_zero(self):
        """Raise error when n is 0 (below minimum of 1)."""
        with pytest.raises(Exception) as exc_info:
            parse_input("0\n")

    def test_parse_input_error_n_out_of_range_negative(self):
        """Raise error when n is negative."""
        with pytest.raises(Exception) as exc_info:
            parse_input("-1\n1 2\n")

    def test_parse_input_error_n_out_of_range_too_large(self):
        """Raise error when n exceeds 10^6."""
        with pytest.raises(Exception) as exc_info:
            parse_input("1000001\n1 2\n")

    def test_parse_input_error_capacity_zero(self):
        """Raise error when old_capacity is 0."""
        with pytest.raises(Exception) as exc_info:
            parse_input("1\n0 5\n")

    def test_parse_input_error_capacity_too_large(self):
        """Raise error when new_capacity exceeds 10^9."""
        with pytest.raises(Exception) as exc_info:
            parse_input("1\n5 1000000001\n")

    def test_parse_input_error_negative_capacity(self):
        """Raise error when a capacity is negative."""
        with pytest.raises(Exception) as exc_info:
            parse_input("1\n-1 5\n")


# ===========================================================================
# SECTION 2: solve tests
# ===========================================================================

class TestSolveHappyPath:
    """Happy path tests for solve."""

    def test_solve_single_drive_upgrade(self):
        """Single drive that grows: E = old_capacity."""
        drives = make_drive_list([(5, 10)])
        result = solve(drives)
        assert result == 5, f"Expected 5, got {result}"

    def test_solve_single_drive_downgrade(self):
        """Single drive that shrinks: E = old_capacity."""
        drives = make_drive_list([(10, 5)])
        result = solve(drives)
        assert result == 10, f"Expected 10, got {result}"

    def test_solve_single_drive_same_capacity(self):
        """Single drive with same old and new: E = old_capacity."""
        drives = make_drive_list([(7, 7)])
        result = solve(drives)
        assert result == 7, f"Expected 7, got {result}"

    def test_solve_all_growers(self):
        """Multiple drives all growing. Smallest old_capacity first."""
        # Drives: (1,10), (3,20), (5,30)
        # Growers sorted by old_capacity asc: (1,10), (3,20), (5,30)
        # Simulation: free=0, free-=1=-1, min=-1, free+=10=9
        #             free-=3=6, min=-1, free+=20=26
        #             free-=5=21, min=-1, free+=30=51
        # E = max(0, -(-1)) = 1
        drives = make_drive_list([(1, 10), (3, 20), (5, 30)])
        result = solve(drives)
        assert result == 1, f"Expected 1, got {result}"

    def test_solve_all_shrinkers(self):
        """Multiple drives all shrinking, sorted by new_capacity descending."""
        # Drives: (10,3), (20,5), (30,1)
        # Shrinkers sorted by b desc: (20,5), (10,3), (30,1)
        # Simulation: free=0, free-=20=-20, min=-20, free+=5=-15
        #             free-=10=-25, min=-25, free+=3=-22
        #             free-=30=-52, min=-52, free+=1=-51
        # E = max(0, 52) = 52
        drives = make_drive_list([(10, 3), (20, 5), (30, 1)])
        result = solve(drives)
        assert result >= 0, f"Expected non-negative, got {result}"
        # Verify by simulation
        ordered = greedy_order([(10, 3), (20, 5), (30, 1)])
        assert simulate_swap(result, ordered), (
            f"E={result} does not suffice for greedy order"
        )

    def test_solve_mixed_growers_and_shrinkers(self):
        """Mix of growing and shrinking drives."""
        # (1,100) is a grower, (50,10) is a shrinker, (5,50) is a grower
        drives = make_drive_list([(1, 100), (50, 10), (5, 50)])
        result = solve(drives)
        assert result >= 0
        # Verify the result via simulation in greedy order
        ordered = greedy_order([(1, 100), (50, 10), (5, 50)])
        assert simulate_swap(result, ordered), (
            f"E={result} does not suffice for greedy order {ordered}"
        )

    def test_solve_two_drives_one_grower_one_shrinker(self):
        """Two drives: one grows, one shrinks."""
        # (3, 10) grower, (10, 2) shrinker
        # Greedy: grower first (3,10), then shrinker (10,2)
        # free=0, -3=-3, min=-3, +10=7, -10=-3, min=-3, +2=-1
        # E = 3
        drives = make_drive_list([(3, 10), (10, 2)])
        result = solve(drives)
        assert result == 3, f"Expected 3, got {result}"


class TestSolveEdgeCases:
    """Edge case tests for solve."""

    def test_solve_single_drive_min_capacity(self):
        """Single drive with minimum capacities (1, 1)."""
        drives = make_drive_list([(1, 1)])
        result = solve(drives)
        assert result == 1, f"Expected 1, got {result}"

    def test_solve_single_drive_large_capacity(self):
        """Single drive with large capacities."""
        drives = make_drive_list([(1000000000, 1000000000)])
        result = solve(drives)
        assert result == 1000000000

    def test_solve_all_same_drives(self):
        """All drives identical."""
        drives = make_drive_list([(5, 5), (5, 5), (5, 5)])
        result = solve(drives)
        assert result == 5, f"Expected 5, got {result}"

    def test_solve_grower_then_shrinker_net_zero(self):
        """A grower and shrinker that net to zero total change."""
        drives = make_drive_list([(2, 8), (8, 2)])
        result = solve(drives)
        # Greedy: grower (2,8) first, then shrinker (8,2)
        # free=0, -2=-2, min=-2, +8=6, -8=-2, min=-2, +2=0
        # E = 2
        assert result == 2, f"Expected 2, got {result}"


class TestSolveErrorCases:
    """Error case tests for solve."""

    def test_solve_empty_drive_list(self):
        """Raise error when drives list is empty."""
        with pytest.raises(Exception) as exc_info:
            solve([])


class TestSolveInvariants:
    """Invariant and property-based tests for solve."""

    def test_solve_result_always_nonnegative(self):
        """Invariant: E >= 0 for all valid inputs."""
        test_cases = [
            [(1, 1)],
            [(10, 1)],
            [(1, 10)],
            [(5, 3), (3, 5)],
            [(100, 1), (1, 100), (50, 50)],
        ]
        for tc in test_cases:
            drives = make_drive_list(tc)
            result = solve(drives)
            assert result >= 0, f"E={result} < 0 for drives {tc}"

    def test_solve_result_sufficient_for_greedy_order(self):
        """Invariant: E suffices for the greedy ordering simulation."""
        test_cases = [
            [(5, 10)],
            [(10, 5)],
            [(1, 100), (50, 10), (5, 50)],
            [(10, 3), (20, 5), (30, 1)],
            [(1, 2), (3, 4), (5, 6)],
            [(6, 1), (4, 2), (2, 5)],
        ]
        for tc in test_cases:
            drives = make_drive_list(tc)
            result = solve(drives)
            ordered = greedy_order(tc)
            assert simulate_swap(result, ordered), (
                f"E={result} does not suffice for greedy order on drives {tc}"
            )

    def test_solve_result_at_least_first_old_capacity_in_greedy_order(self):
        """Invariant: E >= old_capacity of the first drive in greedy order."""
        test_cases = [
            [(5, 10)],
            [(10, 5)],
            [(1, 100), (50, 10), (5, 50)],
            [(3, 1), (7, 2), (10, 8)],
        ]
        for tc in test_cases:
            drives = make_drive_list(tc)
            result = solve(drives)
            ordered = greedy_order(tc)
            first_old = ordered[0][0]
            assert result >= first_old, (
                f"E={result} < first_old={first_old} for drives {tc}"
            )

    def test_solve_brute_force_verification_small_cases(self):
        """For small N, verify solve result matches brute-force minimum over all permutations."""
        random.seed(42)
        test_cases = [
            [(1, 2), (3, 1)],
            [(5, 10), (10, 5), (3, 3)],
            [(2, 8), (8, 2), (4, 6)],
            [(1, 1), (2, 2), (3, 3)],
            [(10, 1), (1, 10)],
            [(3, 7), (7, 3), (5, 5), (2, 9)],
        ]
        # Also add some random small cases
        for _ in range(5):
            n = random.randint(2, 5)
            tc = [(random.randint(1, 20), random.randint(1, 20)) for _ in range(n)]
            test_cases.append(tc)

        for tc in test_cases:
            drives = make_drive_list(tc)
            result = solve(drives)
            bf_result = brute_force_min_swap(tc)
            assert result == bf_result, (
                f"solve={result} != brute_force={bf_result} for drives {tc}"
            )

    def test_solve_permutation_invariance(self):
        """Same set of drives in different input orders produce the same result."""
        random.seed(123)
        base_drives = [(3, 10), (10, 2), (5, 5), (1, 8), (7, 3)]
        drives_base = make_drive_list(base_drives)
        base_result = solve(drives_base)

        for _ in range(10):
            shuffled = base_drives[:]
            random.shuffle(shuffled)
            drives_shuffled = make_drive_list(shuffled)
            result = solve(drives_shuffled)
            assert result == base_result, (
                f"Permutation invariance violated: {result} != {base_result} "
                f"for order {shuffled}"
            )

    def test_solve_brute_force_random_cases(self):
        """Additional random small cases verified via brute force."""
        random.seed(999)
        for _ in range(20):
            n = random.randint(1, 6)
            tc = [(random.randint(1, 15), random.randint(1, 15)) for _ in range(n)]
            drives = make_drive_list(tc)
            result = solve(drives)
            bf_result = brute_force_min_swap(tc)
            assert result == bf_result, (
                f"solve={result} != brute_force={bf_result} for drives {tc}"
            )

    def test_solve_e_minus_one_does_not_suffice(self):
        """Verify that E-1 does NOT suffice (proving minimality) for several cases."""
        test_cases = [
            [(5, 10)],
            [(10, 5)],
            [(1, 100), (50, 10), (5, 50)],
            [(3, 10), (10, 2)],
        ]
        for tc in test_cases:
            drives = make_drive_list(tc)
            result = solve(drives)
            if result > 0:
                # E-1 should NOT suffice for ANY ordering
                ordered = greedy_order(tc)
                assert not simulate_swap(result - 1, ordered), (
                    f"E-1={result - 1} suffices for greedy order on drives {tc}, "
                    f"so E={result} is not minimal"
                )


# ===========================================================================
# SECTION 3: main integration tests
# ===========================================================================

class TestMainIntegration:
    """Integration tests for main() using stdin/stdout mocking."""

    def test_main_single_drive(self):
        """main() with single drive input produces correct output."""
        stdin_data = "1\n5 10\n"
        expected_output = "5\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output == expected_output, (
            f"Expected '{expected_output}', got '{output}'"
        )

    def test_main_three_drives(self):
        """main() with three growing drives."""
        stdin_data = "3\n1 2\n3 4\n5 6\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        # Parse the output
        output_stripped = output.strip()
        assert output_stripped.isdigit() or (output_stripped == "0"), (
            f"Output should be a non-negative integer, got '{output_stripped}'"
        )
        result = int(output_stripped)
        assert result >= 0
        # Verify with solve directly
        drives = make_drive_list([(1, 2), (3, 4), (5, 6)])
        expected = solve(drives)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_main_output_format_single_line_with_newline(self):
        """Output is exactly one line containing an integer followed by newline."""
        stdin_data = "1\n5 10\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        # Should match pattern: digits followed by newline, nothing else
        assert re.fullmatch(r'[0-9]+\n', output), (
            f"Output format mismatch: '{repr(output)}'"
        )

    def test_main_output_no_leading_zeros(self):
        """Output has no leading zeros (except for E=0 itself)."""
        stdin_data = "2\n1 1000000000\n1 1000000000\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        output_stripped = output.strip()
        if output_stripped != "0":
            assert not output_stripped.startswith("0"), (
                f"Output has leading zeros: '{output_stripped}'"
            )

    def test_main_mixed_drives_sample(self):
        """main() with a mixed set of growers and shrinkers."""
        # Drives: (1,100), (50,10), (5,50)
        stdin_data = "3\n1 100\n50 10\n5 50\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        result = int(output.strip())
        drives = make_drive_list([(1, 100), (50, 10), (5, 50)])
        expected = solve(drives)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_main_invalid_input_propagates_error(self):
        """main() propagates error from parse_input for invalid stdin."""
        stdin_data = "abc\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with pytest.raises(Exception):
                main()

    def test_main_empty_input_propagates_error(self):
        """main() propagates error for empty stdin."""
        stdin_data = ""
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with pytest.raises(Exception):
                main()

    def test_main_all_shrinkers(self):
        """main() with all shrinking drives produces correct result."""
        stdin_data = "3\n10 3\n20 5\n30 1\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        result = int(output.strip())
        drives = make_drive_list([(10, 3), (20, 5), (30, 1)])
        expected = solve(drives)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_main_result_matches_solve(self):
        """main() output matches solve() for several inputs."""
        test_inputs = [
            ("1\n1 1\n", [(1, 1)]),
            ("2\n3 10\n10 2\n", [(3, 10), (10, 2)]),
            ("4\n5 5\n10 1\n1 10\n3 7\n", [(5, 5), (10, 1), (1, 10), (3, 7)]),
        ]
        for stdin_data, drive_tuples in test_inputs:
            with patch('sys.stdin', io.StringIO(stdin_data)):
                with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                    main()
                    output = mock_stdout.getvalue()
            result = int(output.strip())
            drives = make_drive_list(drive_tuples)
            expected = solve(drives)
            assert result == expected, (
                f"For input '{stdin_data.strip()}': expected {expected}, got {result}"
            )
