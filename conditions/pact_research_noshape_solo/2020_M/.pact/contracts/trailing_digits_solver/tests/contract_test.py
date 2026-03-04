"""
Contract test suite for trailing_digits_solver.

Tests are organized in four tiers:
  Tier 1: min_multiple_with_n_trailing (modular arithmetic core)
  Tier 2: solve (algorithm correctness with brute-force oracle)
  Tier 3: parse_input (input parsing and validation)
  Tier 4: main (end-to-end stdin/stdout)
  Cross-cutting: Invariants (contiguity, arbitrary precision, termination)
"""

import pytest
import sys
import io
from unittest.mock import patch, MagicMock

# Import the component under test
from src.trailing_digits_solver import (
    min_multiple_with_n_trailing,
    solve,
    parse_input,
    main,
)


# =============================================================================
# Helper: brute-force oracle for solve()
# =============================================================================

def brute_force_solve(b, d, a):
    """
    Brute-force oracle: for each multiple k*b <= a (k >= 1),
    count how many consecutive trailing digits equal d,
    and return the maximum across all multiples.
    """
    max_trailing = 0
    k = 1
    while k * b <= a:
        val = k * b
        count = 0
        s = str(val)
        for ch in reversed(s):
            if ch == str(d):
                count += 1
            else:
                break
        if count > max_trailing:
            max_trailing = count
        k += 1
    return max_trailing


def brute_force_min_multiple(b, d, n):
    """
    Brute-force: find smallest positive multiple of b whose last n digits are all d.
    Returns None if no such multiple exists (checked up to a reasonable bound).
    """
    modulus = 10 ** n
    if d == 0:
        repdigit = 0
    else:
        repdigit = int(str(d) * n)
    # Search up to modulus * b multiples (guaranteed to find if exists)
    for k in range(1, modulus + 1):
        val = k * b
        if val % modulus == repdigit:
            return val
    return None


# =============================================================================
# Tier 1: Unit tests for min_multiple_with_n_trailing
# =============================================================================

class TestMinMultipleWithNTrailing:
    """Tier 1: Tests for the core modular arithmetic function."""

    def test_solvable_b2_d4_n1(self):
        """b=2, d=4, n=1 => smallest multiple of 2 ending in 4 is 4."""
        result = min_multiple_with_n_trailing(2, 4, 1, 10, 4)
        assert result == 4, f"Expected 4, got {result}"
        assert result % 2 == 0, "Result must be a multiple of b=2"
        assert result % 10 == 4, "Last digit must be 4"
        assert result > 0, "Result must be positive"

    def test_solvable_b3_d7_n2(self):
        """b=3, d=7, n=2 => smallest multiple of 3 ending in 77 is 177."""
        result = min_multiple_with_n_trailing(3, 7, 2, 100, 77)
        assert result == 177, f"Expected 177, got {result}"
        assert result % 3 == 0, "Result must be a multiple of b=3"
        assert result % 100 == 77, "Last 2 digits must be 77"
        assert result > 0, "Result must be positive"

    def test_solvable_b7_d1_n3(self):
        """b=7, d=1, n=3 => smallest multiple of 7 with last 3 digits = 111."""
        result = min_multiple_with_n_trailing(7, 1, 3, 1000, 111)
        assert result is not None, "A solution must exist"
        assert result % 7 == 0, "Result must be a multiple of b=7"
        assert result % 1000 == 111, "Last 3 digits must be 111"
        assert result > 0, "Result must be positive"
        # Verify minimality via brute-force
        bf = brute_force_min_multiple(7, 1, 3)
        assert result == bf, f"Expected minimum {bf}, got {result}"

    def test_unsolvable_b2_d3_n1(self):
        """b=2, d=3, n=1 => no even number ends in 3."""
        result = min_multiple_with_n_trailing(2, 3, 1, 10, 3)
        assert result is None, f"Expected None, got {result}"

    def test_unsolvable_b5_d3_n1(self):
        """b=5, d=3, n=1 => no multiple of 5 ends in 3."""
        result = min_multiple_with_n_trailing(5, 3, 1, 10, 3)
        assert result is None, f"Expected None, got {result}"

    def test_unsolvable_b10_d3_n1(self):
        """b=10, d=3, n=1 => no multiple of 10 ends in 3."""
        result = min_multiple_with_n_trailing(10, 3, 1, 10, 3)
        assert result is None, f"Expected None, got {result}"

    def test_d0_n1_b3(self):
        """b=3, d=0, n=1 => smallest multiple of 3 ending in 0 is 30."""
        result = min_multiple_with_n_trailing(3, 0, 1, 10, 0)
        assert result == 30, f"Expected 30, got {result}"
        assert result % 3 == 0
        assert result % 10 == 0

    def test_d0_n2_b3(self):
        """b=3, d=0, n=2 => smallest multiple of 3 ending in 00 is 300."""
        result = min_multiple_with_n_trailing(3, 0, 2, 100, 0)
        assert result == 300, f"Expected 300, got {result}"
        assert result % 3 == 0
        assert result % 100 == 0

    def test_b1_d5_n1(self):
        """b=1, d=5, n=1 => smallest multiple of 1 ending in 5 is 5."""
        result = min_multiple_with_n_trailing(1, 5, 1, 10, 5)
        assert result == 5, f"Expected 5, got {result}"

    def test_b1_d9_n3(self):
        """b=1, d=9, n=3 => smallest multiple of 1 ending in 999 is 999."""
        result = min_multiple_with_n_trailing(1, 9, 3, 1000, 999)
        assert result == 999, f"Expected 999, got {result}"

    def test_b1_d1_n5(self):
        """b=1, d=1, n=5 => smallest multiple of 1 ending in 11111 is 11111."""
        result = min_multiple_with_n_trailing(1, 1, 5, 100000, 11111)
        assert result == 11111, f"Expected 11111, got {result}"

    def test_b7_d7_n1(self):
        """b=7, d=7, n=1 => smallest multiple of 7 ending in 7 is 7."""
        result = min_multiple_with_n_trailing(7, 7, 1, 10, 7)
        assert result == 7, f"Expected 7, got {result}"

    def test_b4_d4_n2(self):
        """b=4, d=4, n=2 => smallest multiple of 4 ending in 44 is 44."""
        result = min_multiple_with_n_trailing(4, 4, 2, 100, 44)
        assert result == 44, f"Expected 44, got {result}"

    def test_b8_d8_n2(self):
        """b=8, d=8, n=2 => smallest multiple of 8 ending in 88 is 88."""
        result = min_multiple_with_n_trailing(8, 8, 2, 100, 88)
        assert result == 88, f"Expected 88, got {result}"

    def test_minimality_property(self):
        """Verify minimality: no smaller positive multiple satisfies the trailing condition."""
        test_cases = [
            (2, 4, 1, 10, 4),
            (3, 7, 2, 100, 77),
            (7, 7, 1, 10, 7),
            (13, 9, 2, 100, 99),
            (6, 6, 3, 1000, 666),
        ]
        for b, d, n, modulus, repdigit in test_cases:
            result = min_multiple_with_n_trailing(b, d, n, modulus, repdigit)
            if result is not None:
                bf = brute_force_min_multiple(b, d, n)
                assert result == bf, (
                    f"Minimality violation for b={b}, d={d}, n={n}: "
                    f"got {result}, brute-force says {bf}"
                )

    def test_arbitrary_precision_large_n(self):
        """Invariant: handles large n (20 digits) with arbitrary-precision integers."""
        n = 20
        modulus = 10 ** n
        repdigit = int("7" * n)
        result = min_multiple_with_n_trailing(7, 7, n, modulus, repdigit)
        assert result is not None, "Solution should exist for b=7, d=7"
        assert result % 7 == 0, "Result must be a multiple of 7"
        assert result % modulus == repdigit, f"Last {n} digits must be all 7s"
        assert result > 0, "Result must be positive"


# =============================================================================
# Tier 2: Unit tests for solve
# =============================================================================

class TestSolve:
    """Tier 2: Tests for the solve algorithm."""

    def test_b2_d4_a100(self):
        """b=2, d=4, a=100 => result is 2 (4 and 44 both <=100, but 444>100)."""
        result = solve(2, 4, 100)
        assert result == 2, f"Expected 2, got {result}"

    def test_b1_d1_a111(self):
        """b=1, d=1, a=111 => multiples include 1, 11, 111. Result is 3."""
        result = solve(1, 1, 111)
        assert result == 3, f"Expected 3, got {result}"

    def test_b1_d1_a110(self):
        """b=1, d=1, a=110 => 111 > 110, so result is 2."""
        result = solve(1, 1, 110)
        assert result == 2, f"Expected 2, got {result}"

    def test_unsolvable_b2_d3(self):
        """b=2, d=3 => no even number ends in 3, result is 0."""
        result = solve(2, 3, 1000)
        assert result == 0, f"Expected 0, got {result}"

    def test_unsolvable_b5_d1(self):
        """b=5, d=1 => no multiple of 5 ends in 1, result is 0."""
        result = solve(5, 1, 10000)
        assert result == 0, f"Expected 0, got {result}"

    def test_d0_b3_a1000(self):
        """b=3, d=0, a=1000 => 30 (1 zero), 300 (2 zeros), 3000>1000. Result is 2."""
        result = solve(3, 0, 1000)
        assert result == 2, f"Expected 2, got {result}"

    def test_b1_d9_a9(self):
        """b=1, d=9, a=9 => 9 ends in 9, 99>9. Result is 1."""
        result = solve(1, 9, 9)
        assert result == 1, f"Expected 1, got {result}"

    def test_b1_d9_a8(self):
        """b=1, d=9, a=8 => 9 > 8. Result is 0."""
        result = solve(1, 9, 8)
        assert result == 0, f"Expected 0, got {result}"

    def test_b7_d7_a7777(self):
        """b=7, d=7, a=7777 => 7, 77, 777, 7777 all work. Result is 4."""
        result = solve(7, 7, 7777)
        assert result == 4, f"Expected 4, got {result}"

    def test_b10_d0_a100(self):
        """b=10, d=0, a=100 => 10 (1 zero), 100 (2 zeros). Result is 2."""
        result = solve(10, 0, 100)
        assert result == 2, f"Expected 2, got {result}"

    def test_b10_d0_a99(self):
        """b=10, d=0, a=99 => 10 ends in 0, 100>99. Result is 1."""
        result = solve(10, 0, 99)
        assert result == 1, f"Expected 1, got {result}"

    def test_b3_d3_a33333(self):
        """b=3, d=3, a=33333 => 3, 33, 333, 3333, 33333 all work. Result is 5."""
        result = solve(3, 3, 33333)
        assert result == 5, f"Expected 5, got {result}"

    def test_result_nonnegative(self):
        """Postcondition: result >= 0 for valid inputs."""
        result = solve(13, 5, 1)
        assert result >= 0, f"Result must be non-negative, got {result}"

    def test_brute_force_oracle_small_space(self):
        """Verify solve() against brute-force oracle for b in [1..20], d in [0..9], small a."""
        failures = []
        for b in range(1, 21):
            for d in range(0, 10):
                for a in [1, 2, 5, 10, 50, 100, 200]:
                    expected = brute_force_solve(b, d, a)
                    actual = solve(b, d, a)
                    if actual != expected:
                        failures.append(
                            f"b={b}, d={d}, a={a}: expected {expected}, got {actual}"
                        )
        assert not failures, (
            f"Brute-force oracle mismatches ({len(failures)}):\n"
            + "\n".join(failures[:20])
        )

    def test_contiguous_range_invariant(self):
        """
        Invariant: if solve returns n, then for all m in 1..n there exists
        a valid multiple k*b <= a with m trailing d's.
        """
        test_cases = [
            (3, 3, 33333),
            (7, 7, 7777),
            (2, 4, 100),
            (1, 1, 111),
            (6, 6, 666666),
        ]
        for b, d, a in test_cases:
            n = solve(b, d, a)
            for m in range(1, n + 1):
                modulus_m = 10 ** m
                if d == 0:
                    repdigit_m = 0
                else:
                    repdigit_m = int(str(d) * m)
                result = min_multiple_with_n_trailing(b, d, m, modulus_m, repdigit_m)
                assert result is not None, (
                    f"Contiguity violation: b={b}, d={d}, a={a}, n={n}, m={m}: "
                    f"no qualifying multiple found"
                )
                assert result <= a, (
                    f"Contiguity violation: b={b}, d={d}, a={a}, n={n}, m={m}: "
                    f"min multiple {result} exceeds a={a}"
                )

    def test_large_a_termination(self):
        """Invariant: solve terminates for very large a values."""
        # 30-digit repdigit of 1s
        a = int("1" * 30)
        result = solve(1, 1, a)
        assert result == 30, f"Expected 30, got {result}"

    def test_large_a_termination_b7(self):
        """Invariant: solve terminates for large a with b=7."""
        a = int("7" * 15)
        result = solve(7, 7, a)
        assert result == 15, f"Expected 15, got {result}"


# =============================================================================
# Tier 3: Unit tests for parse_input
# =============================================================================

class TestParseInput:
    """Tier 3: Tests for input parsing and validation."""

    def test_valid_simple(self):
        """parse_input: valid input '2 4 100'."""
        result = parse_input("2 4 100")
        assert result.b == 2, f"Expected b=2, got {result.b}"
        assert result.d == 4, f"Expected d=4, got {result.d}"
        assert result.a == 100, f"Expected a=100, got {result.a}"

    def test_valid_extra_whitespace(self):
        """parse_input: extra whitespace is handled correctly."""
        result = parse_input("  7  0  999  ")
        assert result.b == 7, f"Expected b=7, got {result.b}"
        assert result.d == 0, f"Expected d=0, got {result.d}"
        assert result.a == 999, f"Expected a=999, got {result.a}"

    def test_valid_newline_separated(self):
        """parse_input: tokens separated by newlines."""
        result = parse_input("1\n5\n1000")
        assert result.b == 1
        assert result.d == 5
        assert result.a == 1000

    def test_valid_boundary_d0(self):
        """parse_input: d=0 lower boundary."""
        result = parse_input("1 0 1")
        assert result.b == 1
        assert result.d == 0
        assert result.a == 1

    def test_valid_boundary_d9(self):
        """parse_input: d=9 upper boundary."""
        result = parse_input("1 9 1")
        assert result.d == 9

    def test_valid_large_values(self):
        """parse_input: handles large integer values."""
        big_a = "9" * 100
        result = parse_input(f"1 5 {big_a}")
        assert result.b == 1
        assert result.d == 5
        assert result.a == int(big_a)

    def test_error_wrong_token_count_too_few(self):
        """parse_input: only 2 tokens raises an error."""
        with pytest.raises(Exception):
            parse_input("2 4")

    def test_error_wrong_token_count_too_many(self):
        """parse_input: 4 tokens raises an error."""
        with pytest.raises(Exception):
            parse_input("2 4 100 5")

    def test_error_wrong_token_count_empty(self):
        """parse_input: empty string raises an error."""
        with pytest.raises(Exception):
            parse_input("")

    def test_error_wrong_token_count_one(self):
        """parse_input: single token raises an error."""
        with pytest.raises(Exception):
            parse_input("42")

    def test_error_non_integer_token(self):
        """parse_input: non-integer token raises an error."""
        with pytest.raises(Exception):
            parse_input("abc 4 100")

    def test_error_non_integer_token_middle(self):
        """parse_input: non-integer in middle position raises an error."""
        with pytest.raises(Exception):
            parse_input("2 xyz 100")

    def test_error_non_integer_token_float(self):
        """parse_input: float token raises an error."""
        with pytest.raises(Exception):
            parse_input("2 4 10.5")

    def test_error_b_out_of_range_zero(self):
        """parse_input: b=0 raises an error (b must be >= 1)."""
        with pytest.raises(Exception):
            parse_input("0 4 100")

    def test_error_d_out_of_range_negative(self):
        """parse_input: d=-1 raises an error."""
        with pytest.raises(Exception):
            parse_input("1 -1 100")

    def test_error_d_out_of_range_10(self):
        """parse_input: d=10 raises an error."""
        with pytest.raises(Exception):
            parse_input("1 10 100")

    def test_error_a_out_of_range_zero(self):
        """parse_input: a=0 raises an error."""
        with pytest.raises(Exception):
            parse_input("1 4 0")


# =============================================================================
# Tier 4: End-to-end tests for main
# =============================================================================

class TestMain:
    """Tier 4: End-to-end tests for main() with stdin/stdout capture."""

    def test_basic_e2e(self):
        """main: reads '2 4 100' from stdin, writes correct result to stdout."""
        with patch("sys.stdin", io.StringIO("2 4 100")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.strip() == "2", f"Expected '2', got '{output.strip()}'"

    def test_output_ends_with_newline(self):
        """main: output ends with a newline character."""
        with patch("sys.stdin", io.StringIO("1 1 111")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.endswith("\n"), f"Output should end with newline, got repr: {repr(output)}"
        assert output == "3\n", f"Expected '3\\n', got {repr(output)}"

    def test_unsolvable_e2e(self):
        """main: reads '2 3 1000', writes '0' to stdout."""
        with patch("sys.stdin", io.StringIO("2 3 1000")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.strip() == "0", f"Expected '0', got '{output.strip()}'"

    def test_single_line_output(self):
        """main: output is exactly one line (no extra lines)."""
        with patch("sys.stdin", io.StringIO("7 7 7777")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        lines = output.rstrip("\n").split("\n")
        assert len(lines) == 1, f"Expected exactly 1 line, got {len(lines)}: {lines}"
        assert lines[0] == "4", f"Expected '4', got '{lines[0]}'"

    def test_d0_e2e(self):
        """main: d=0 case works end-to-end."""
        with patch("sys.stdin", io.StringIO("3 0 1000")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.strip() == "2", f"Expected '2', got '{output.strip()}'"

    def test_b1_d5_a55555_e2e(self):
        """main: b=1, d=5, a=55555 => 5, 55, 555, 5555, 55555 => result is 5."""
        with patch("sys.stdin", io.StringIO("1 5 55555")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.strip() == "5", f"Expected '5', got '{output.strip()}'"

    def test_newline_separated_input(self):
        """main: input with newline separators works."""
        with patch("sys.stdin", io.StringIO("10\n0\n100")):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
        assert output.strip() == "2", f"Expected '2', got '{output.strip()}'"


# =============================================================================
# Cross-cutting invariant tests
# =============================================================================

class TestInvariants:
    """Cross-cutting invariant verification."""

    def test_result_is_nonneg_for_various_inputs(self):
        """solve() always returns a non-negative integer."""
        test_cases = [
            (1, 0, 1), (1, 9, 1), (2, 3, 1), (10, 5, 10),
            (50, 0, 1), (7, 7, 7), (13, 5, 1),
        ]
        for b, d, a in test_cases:
            result = solve(b, d, a)
            assert isinstance(result, int), f"solve({b},{d},{a}) should return int, got {type(result)}"
            assert result >= 0, f"solve({b},{d},{a}) returned negative: {result}"

    def test_postcondition_trailing_digits_property(self):
        """
        For solve(b, d, a) returning n > 0, verify there exists k*b <= a
        with n trailing d digits.
        """
        test_cases = [
            (2, 4, 100),
            (3, 3, 33333),
            (7, 7, 7777),
            (1, 1, 111),
            (10, 0, 100),
        ]
        for b, d, a in test_cases:
            n = solve(b, d, a)
            if n > 0:
                modulus = 10 ** n
                if d == 0:
                    repdigit = 0
                else:
                    repdigit = int(str(d) * n)
                min_mult = min_multiple_with_n_trailing(b, d, n, modulus, repdigit)
                assert min_mult is not None, (
                    f"solve({b},{d},{a})={n} but no qualifying multiple found"
                )
                assert min_mult <= a, (
                    f"solve({b},{d},{a})={n} but min multiple {min_mult} > a={a}"
                )
                assert min_mult % b == 0, (
                    f"Result {min_mult} is not a multiple of b={b}"
                )
                assert min_mult % modulus == repdigit, (
                    f"Result {min_mult} does not have {n} trailing {d}s"
                )

    def test_postcondition_no_better_solution(self):
        """
        For solve(b, d, a) returning n, verify that n+1 trailing digits
        is NOT achievable (either no solution or min multiple exceeds a).
        """
        test_cases = [
            (2, 4, 100),
            (1, 1, 111),
            (7, 7, 7777),
            (3, 0, 1000),
            (10, 0, 99),
        ]
        for b, d, a in test_cases:
            n = solve(b, d, a)
            n_plus_1 = n + 1
            modulus = 10 ** n_plus_1
            if d == 0:
                repdigit = 0
            else:
                repdigit = int(str(d) * n_plus_1)
            # Check: either repdigit > a, or no solution, or min solution > a
            if repdigit > a:
                # Repdigit itself exceeds a, so no solution possible
                continue
            min_mult = min_multiple_with_n_trailing(b, d, n_plus_1, modulus, repdigit)
            if min_mult is None:
                continue  # No solution exists - correct
            assert min_mult > a, (
                f"solve({b},{d},{a})={n} but n+1={n_plus_1} has qualifying "
                f"multiple {min_mult} <= a={a}"
            )

    def test_zero_result_means_no_trailing_d(self):
        """If solve returns 0, then no multiple of b in [b, a] ends in digit d."""
        test_cases = [
            (2, 3, 1000),
            (5, 1, 10000),
            (1, 9, 8),
        ]
        for b, d, a in test_cases:
            result = solve(b, d, a)
            assert result == 0, f"Expected 0 for b={b}, d={d}, a={a}, got {result}"
            # Verify via brute-force
            bf = brute_force_solve(b, d, a)
            assert bf == 0, (
                f"Brute-force found {bf} trailing {d}s for b={b}, a={a}"
            )

    def test_min_multiple_returns_positive(self):
        """If min_multiple_with_n_trailing returns a value, it's always positive."""
        test_cases = [
            (1, 0, 1, 10, 0),
            (1, 0, 2, 100, 0),
            (5, 5, 1, 10, 5),
            (10, 0, 1, 10, 0),
            (100, 0, 3, 1000, 0),
        ]
        for b, d, n, modulus, repdigit in test_cases:
            result = min_multiple_with_n_trailing(b, d, n, modulus, repdigit)
            if result is not None:
                assert result > 0, (
                    f"min_multiple({b},{d},{n}) returned non-positive: {result}"
                )

    def test_min_multiple_brute_force_agreement(self):
        """
        Cross-check min_multiple_with_n_trailing against brute-force
        for a range of small inputs.
        """
        failures = []
        for b in range(1, 16):
            for d in range(0, 10):
                for n in range(1, 4):
                    modulus = 10 ** n
                    if d == 0:
                        repdigit = 0
                    else:
                        repdigit = int(str(d) * n)
                    result = min_multiple_with_n_trailing(b, d, n, modulus, repdigit)
                    bf = brute_force_min_multiple(b, d, n)
                    if result != bf:
                        failures.append(
                            f"b={b}, d={d}, n={n}: got {result}, bf={bf}"
                        )
        assert not failures, (
            f"Brute-force mismatches ({len(failures)}):\n"
            + "\n".join(failures[:20])
        )

    def test_k_positive_invariant_d0(self):
        """
        Invariant: k is always positive. When d=0 and repdigit=0,
        the congruence k*b ≡ 0 has trivial solution k=0 which must be
        replaced with k=modulus//gcd. The result k*b must be positive.
        """
        for b in [1, 2, 3, 5, 7, 10, 100]:
            for n in [1, 2, 3]:
                modulus = 10 ** n
                result = min_multiple_with_n_trailing(b, 0, n, modulus, 0)
                if result is not None:
                    assert result > 0, (
                        f"d=0 k-positive invariant violated: b={b}, n={n}, "
                        f"result={result}"
                    )
                    assert result % modulus == 0, (
                        f"d=0 trailing zeros check failed: b={b}, n={n}, "
                        f"result={result}"
                    )
