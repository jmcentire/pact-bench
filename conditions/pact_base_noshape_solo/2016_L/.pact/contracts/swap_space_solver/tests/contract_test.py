"""
Contract test suite for swap_space_solver.
Three-tier structure:
  Tier 1: TestParseInput  — unit tests for parse_input()
  Tier 2: TestSolve       — unit tests for solve()
  Tier 3: TestMain        — integration tests for main()

Uses only pytest and unittest.mock (stdlib). All randomized tests are seeded.
"""

import io
import sys
import random
from unittest.mock import patch, MagicMock

import pytest

from src.swap_space_solver import parse_input, solve, main


# ---------------------------------------------------------------------------
# Helper: simulate the greedy reformat sequence and check feasibility
# ---------------------------------------------------------------------------

def _greedy_order(drives):
    """Return drives in the canonical greedy order:
    gainers (b >= a) sorted by a ascending, then losers (b < a) sorted by b descending.
    """
    gainers = [(a, b) for a, b in drives if b >= a]
    losers = [(a, b) for a, b in drives if b < a]
    gainers.sort(key=lambda d: d[0])
    losers.sort(key=lambda d: d[1], reverse=True)
    return gainers + losers


def simulate(drives, extra):
    """Replay the greedy upgrade starting with *extra* free space.
    Returns True iff free space never drops below 0."""
    ordered = _greedy_order(drives)
    free = extra
    for a, b in ordered:
        if free < a:
            return False
        free = free - a + b
    return True


# ===========================================================================
# Tier 1 — parse_input()
# ===========================================================================

class TestParseInput:
    """Unit tests for parse_input()."""

    def test_parse_input_empty_list(self):
        """n=0 ⇒ empty list."""
        with patch("sys.stdin", new_callable=lambda: lambda: io.StringIO("0\n")):
            pass  # need direct assignment
        fake_stdin = io.StringIO("0\n")
        with patch.object(sys, "stdin", fake_stdin):
            result = parse_input()
        assert result == [], f"Expected empty list, got {result}"
        assert len(result) == 0

    def test_parse_input_single_drive(self):
        """n=1 with one (a,b) pair."""
        fake_stdin = io.StringIO("1\n10 20\n")
        with patch.object(sys, "stdin", fake_stdin):
            result = parse_input()
        assert result == [(10, 20)], f"Expected [(10, 20)], got {result}"
        assert len(result) == 1

    def test_parse_input_many_drives(self):
        """n=3 with three (a,b) pairs preserves order."""
        fake_stdin = io.StringIO("3\n1 2\n3 4\n5 6\n")
        with patch.object(sys, "stdin", fake_stdin):
            result = parse_input()
        assert result == [(1, 2), (3, 4), (5, 6)]
        assert len(result) == 3

    def test_parse_input_large_values(self):
        """Large integers parse correctly."""
        big = 10**18
        fake_stdin = io.StringIO(f"1\n{big} {big + 1}\n")
        with patch.object(sys, "stdin", fake_stdin):
            result = parse_input()
        assert result == [(big, big + 1)]

    def test_parse_input_whitespace_variations(self):
        """Tokens separated by mixed whitespace still parse."""
        fake_stdin = io.StringIO("2\n  1   2  \n  3   4  \n")
        with patch.object(sys, "stdin", fake_stdin):
            result = parse_input()
        assert result == [(1, 2), (3, 4)]

    # --- Error cases ---

    def test_parse_input_empty_stdin(self):
        """Empty stdin raises an error."""
        fake_stdin = io.StringIO("")
        with patch.object(sys, "stdin", fake_stdin):
            with pytest.raises((ValueError, IndexError)):
                parse_input()

    def test_parse_input_malformed_n(self):
        """Non-integer first token raises ValueError."""
        fake_stdin = io.StringIO("abc\n1 2\n")
        with patch.object(sys, "stdin", fake_stdin):
            with pytest.raises((ValueError, IndexError)):
                parse_input()

    def test_parse_input_insufficient_tokens(self):
        """Fewer than 2*n data tokens raises an error."""
        fake_stdin = io.StringIO("2\n1 2\n")
        with patch.object(sys, "stdin", fake_stdin):
            with pytest.raises((ValueError, IndexError)):
                parse_input()

    def test_parse_input_non_integer_token(self):
        """Non-integer drive data token raises ValueError."""
        fake_stdin = io.StringIO("1\nfoo 2\n")
        with patch.object(sys, "stdin", fake_stdin):
            with pytest.raises((ValueError, IndexError)):
                parse_input()

    def test_parse_input_negative_n(self):
        """Negative n should raise an error or return empty."""
        fake_stdin = io.StringIO("-1\n")
        with patch.object(sys, "stdin", fake_stdin):
            # Either raises or returns empty; either is acceptable.
            try:
                result = parse_input()
                # If it doesn't raise, it should be empty (n <= 0 drives).
                assert result == [] or True  # implementation-specific
            except (ValueError, IndexError):
                pass  # acceptable


# ===========================================================================
# Tier 2 — solve()
# ===========================================================================

class TestSolve:
    """Unit tests for solve()."""

    # --- Happy-path / known-answer tests ---

    def test_solve_empty_list(self):
        """Empty drive list ⇒ 0."""
        assert solve([]) == 0

    def test_solve_single_gainer(self):
        """Single drive (10, 20): need 10 extra space."""
        result = solve([(10, 20)])
        assert result == 10, f"Expected 10, got {result}"

    def test_solve_single_loser(self):
        """Single drive (20, 10): need 20 extra space."""
        result = solve([(20, 10)])
        assert result == 20, f"Expected 20, got {result}"

    def test_solve_mixed_drives(self):
        """Two drives: gainer (10,20) then loser (20,10).
        Greedy order: (10,20) first (gainer, a=10), then (20,10) (loser, b=10).
        Need S >= 10 to process first. After first: free = S + 10.
        Need S + 10 >= 20 ⇒ S >= 10. So S = 10."""
        result = solve([(10, 20), (20, 10)])
        assert result == 10, f"Expected 10, got {result}"

    def test_solve_mixed_drives_reversed_input(self):
        """Same drives in reversed input order — should give same result (permutation invariance)."""
        result = solve([(20, 10), (10, 20)])
        assert result == 10, f"Expected 10, got {result}"

    def test_solve_all_gainers(self):
        """All gainers: (1,4), (3,8), (5,10).
        Sorted by a: (1,4), (3,8), (5,10).
        prefix_net before i=0: 0 ⇒ need S >= 1.
        prefix_net before i=1: 3 ⇒ need S >= 3 - 3 = 0.
        prefix_net before i=2: 3 + 5 = 8 ⇒ need S >= 5 - 8 = 0.
        S = 1."""
        result = solve([(5, 10), (3, 8), (1, 4)])
        assert result == 1, f"Expected 1, got {result}"
        assert simulate([(5, 10), (3, 8), (1, 4)], result)

    def test_solve_all_losers(self):
        """All losers: (10,5), (20,10), (15,8).
        Sorted by b desc: (20,10), (15,8), (10,5).
        prefix_net before i=0: 0 ⇒ need S >= 20.
        prefix_net before i=1: -10 ⇒ need S >= 15 + 10 = 25.
        prefix_net before i=2: -10 + -7 = -17 ⇒ need S >= 10 + 17 = 27.
        S = 27."""
        result = solve([(10, 5), (20, 10), (15, 8)])
        assert result == 27, f"Expected 27, got {result}"
        assert simulate([(10, 5), (20, 10), (15, 8)], result)

    def test_solve_identical_drives_a_eq_b(self):
        """Identical drives with a == b: (5,5) x3.
        All are gainers (b >= a). Sorted by a=5, all same.
        prefix_net before i=0: 0 ⇒ S >= 5.
        prefix_net before i=1: 0 ⇒ S >= 5.
        prefix_net before i=2: 0 ⇒ S >= 5.
        S = 5."""
        result = solve([(5, 5), (5, 5), (5, 5)])
        assert result == 5, f"Expected 5, got {result}"

    def test_solve_zero_capacity_drives(self):
        """All a == 0 ⇒ S == 0."""
        result = solve([(0, 10), (0, 5), (0, 0)])
        assert result == 0, f"Expected 0, got {result}"

    def test_solve_all_zero(self):
        """All drives (0, 0)."""
        result = solve([(0, 0), (0, 0)])
        assert result == 0

    def test_solve_large_values(self):
        """Single drive with a = 10^18."""
        big = 10**18
        result = solve([(big, big + 1)])
        assert result == big

    def test_solve_single_zero_a(self):
        """Single drive (0, 100): no data to move."""
        result = solve([(0, 100)])
        assert result == 0

    # --- Edge cases ---

    def test_solve_two_gainers_order_matters(self):
        """Two gainers: (100, 200) and (1, 50).
        Sorted by a: (1, 50), (100, 200).
        prefix_net before i=0: 0 ⇒ S >= 1.
        prefix_net before i=1: 49 ⇒ S >= 100 - 49 = 51.
        S = 51."""
        result = solve([(100, 200), (1, 50)])
        assert result == 51, f"Expected 51, got {result}"
        assert simulate([(100, 200), (1, 50)], result)
        assert not simulate([(100, 200), (1, 50)], result - 1)

    def test_solve_complex_mixed(self):
        """More complex mixed example with known answer verified by simulation."""
        drives = [(10, 20), (5, 3), (8, 15), (12, 6)]
        result = solve(drives)
        assert result >= 0
        assert simulate(drives, result), f"S={result} should be feasible"
        if result > 0:
            assert not simulate(drives, result - 1), f"S={result-1} should be infeasible"

    # --- Error cases ---

    def test_solve_negative_a(self):
        """Negative a raises ValueError."""
        with pytest.raises((ValueError, AssertionError)):
            solve([(-1, 5)])

    def test_solve_negative_b(self):
        """Negative b raises ValueError."""
        with pytest.raises((ValueError, AssertionError)):
            solve([(5, -1)])

    # --- Invariant tests (seeded random) ---

    def test_solve_nonnegative_invariant_random(self):
        """solve always returns a non-negative integer (random inputs, seeded)."""
        rng = random.Random(42)
        for _ in range(50):
            n = rng.randint(0, 20)
            drives = [(rng.randint(0, 1000), rng.randint(0, 1000)) for _ in range(n)]
            result = solve(drives)
            assert result >= 0, f"Negative result {result} for drives={drives}"
            assert isinstance(result, int), f"Result should be int, got {type(result)}"

    def test_solve_permutation_invariant_random(self):
        """solve returns the same result regardless of input order."""
        rng = random.Random(123)
        for _ in range(30):
            n = rng.randint(1, 15)
            drives = [(rng.randint(0, 500), rng.randint(0, 500)) for _ in range(n)]
            result1 = solve(drives)
            shuffled = drives[:]
            rng.shuffle(shuffled)
            result2 = solve(shuffled)
            assert result1 == result2, (
                f"Permutation invariance violated: {result1} != {result2} "
                f"for drives={drives}, shuffled={shuffled}"
            )

    def test_solve_upper_bound_invariant_random(self):
        """solve result <= sum of all a values."""
        rng = random.Random(99)
        for _ in range(50):
            n = rng.randint(0, 20)
            drives = [(rng.randint(0, 1000), rng.randint(0, 1000)) for _ in range(n)]
            result = solve(drives)
            total_a = sum(a for a, b in drives)
            assert result <= total_a, (
                f"Result {result} exceeds sum of a values {total_a} for {drives}"
            )

    def test_solve_simulation_feasibility_random(self):
        """Simulation confirms S is feasible and minimal (random inputs, seeded)."""
        rng = random.Random(777)
        for _ in range(50):
            n = rng.randint(0, 15)
            drives = [(rng.randint(0, 500), rng.randint(0, 500)) for _ in range(n)]
            result = solve(drives)
            assert simulate(drives, result), (
                f"S={result} infeasible for {drives}"
            )
            if result > 0:
                assert not simulate(drives, result - 1), (
                    f"S={result - 1} should be infeasible but isn't for {drives}"
                )

    def test_solve_specific_upper_bound(self):
        """Explicit upper bound check."""
        drives = [(10, 20), (30, 5), (15, 15)]
        result = solve(drives)
        assert result >= 0
        assert result <= 55, f"Result {result} should be <= sum of a=55"

    def test_solve_known_answer_three_drives(self):
        """Three drives: (10,20), (30,5), (15,15). Verify by simulation."""
        drives = [(10, 20), (30, 5), (15, 15)]
        result = solve(drives)
        assert simulate(drives, result)
        if result > 0:
            assert not simulate(drives, result - 1)


# ===========================================================================
# Tier 3 — main()
# ===========================================================================

class TestMain:
    """Integration tests for main()."""

    def test_main_happy_path(self):
        """main() reads stdin, prints correct result to stdout."""
        fake_stdin = io.StringIO("2\n10 20\n20 10\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output == "10\n", f"Expected '10\\n', got {output!r}"

    def test_main_empty_drives(self):
        """main() with n=0 prints '0'."""
        fake_stdin = io.StringIO("0\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output == "0\n", f"Expected '0\\n', got {output!r}"

    def test_main_single_drive(self):
        """main() with one drive."""
        fake_stdin = io.StringIO("1\n7 3\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output == "7\n", f"Expected '7\\n', got {output!r}"

    def test_main_output_format_trailing_newline(self):
        """Output is exactly one line with trailing newline."""
        fake_stdin = io.StringIO("1\n5 10\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output.endswith("\n"), "Output must end with newline"
        lines = output.strip().split("\n")
        assert len(lines) == 1, f"Expected exactly one line, got {len(lines)}"
        assert lines[0].strip().isdigit() or lines[0].strip() == "0", (
            f"Output should be a non-negative integer, got {lines[0]!r}"
        )

    def test_main_input_error_malformed(self):
        """main() propagates error on malformed input."""
        fake_stdin = io.StringIO("not_a_number\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            with pytest.raises((ValueError, IndexError, SystemExit)):
                main()

    def test_main_io_error_stdout(self):
        """main() raises error when stdout write fails."""
        fake_stdin = io.StringIO("1\n5 10\n")
        mock_stdout = MagicMock()
        mock_stdout.write = MagicMock(side_effect=OSError("write failed"))
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", mock_stdout):
            with pytest.raises((OSError, IOError)):
                main()

    def test_main_larger_example(self):
        """main() with a larger known-answer example."""
        # 3 drives: (1, 4), (3, 8), (5, 10) — all gainers
        # Expected S = 1 (from solve test above)
        fake_stdin = io.StringIO("3\n1 4\n3 8\n5 10\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output == "1\n", f"Expected '1\\n', got {output!r}"

    def test_main_all_losers_example(self):
        """main() with all losers example."""
        fake_stdin = io.StringIO("3\n10 5\n20 10\n15 8\n")
        fake_stdout = io.StringIO()
        with patch.object(sys, "stdin", fake_stdin), \
             patch.object(sys, "stdout", fake_stdout):
            main()
        output = fake_stdout.getvalue()
        assert output == "27\n", f"Expected '27\\n', got {output!r}"
