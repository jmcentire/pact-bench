"""
Contract tests for posterize_solver module.

Tests verify the contract for: parse_input, build_prefix_sums, cost, solve, main.
All dependencies are mocked; tests verify behavior at boundaries.
"""

import io
import sys
import pytest
from unittest.mock import patch

# Import the component under test
from src.posterize_solver import (
    parse_input,
    build_prefix_sums,
    cost,
    solve,
    main,
)


# ============================================================
# Helper: build prefix sums from a list of (r, p) tuples
# Used by tests to set up known prefix sum arrays
# ============================================================

def _make_prefix_sums(values):
    """Manually compute prefix sums for test setup (not using the SUT)."""
    d = len(values)
    s0 = [0] * (d + 1)
    s1 = [0] * (d + 1)
    s2 = [0] * (d + 1)
    for i, (r, p) in enumerate(values):
        s0[i + 1] = s0[i] + p
        s1[i + 1] = s1[i] + p * r
        s2[i + 1] = s2[i] + p * r * r
    return s0, s1, s2


def _extract_parse_result(result):
    """Extract d, k, values from parse_input result regardless of struct vs tuple."""
    if hasattr(result, 'd'):
        d = result.d
        k = result.k
        values = result.values
    else:
        d, k, values = result[0], result[1], result[2]
    # Normalize values to list of tuples
    if values and hasattr(values[0], 'r'):
        values = [(v.r, v.p) for v in values]
    else:
        values = [(v[0], v[1]) for v in values]
    return d, k, values


def _extract_prefix_sums(result):
    """Extract s0, s1, s2 from build_prefix_sums result."""
    if hasattr(result, 's0'):
        return list(result.s0), list(result.s1), list(result.s2)
    else:
        return list(result[0]), list(result[1]), list(result[2])


def _make_values_arg(tuples):
    """
    Create the values argument for build_prefix_sums.
    Tries to match whatever type the module expects (tuples or structs).
    We pass plain tuples; if the module uses namedtuples or similar, 
    tuples should still work since contract says RedPixelPair is a struct.
    """
    return tuples


# ============================================================
# Tests for parse_input()
# ============================================================

class TestParseInput:
    """Tests for parse_input function."""

    def test_parse_input_happy_basic(self):
        """Parse a well-formed input with 3 distinct values and k=2."""
        stdin_data = "3 2\n10 100\n20 200\n30 300\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            result = parse_input()
        d, k, values = _extract_parse_result(result)
        assert d == 3, f"Expected d=3, got {d}"
        assert k == 2, f"Expected k=2, got {k}"
        assert len(values) == 3, f"Expected 3 values, got {len(values)}"
        assert values == [(10, 100), (20, 200), (30, 300)], f"Unexpected values: {values}"

    def test_parse_input_happy_single(self):
        """Parse input with a single distinct value d=1 k=1."""
        stdin_data = "1 1\n128 50\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            result = parse_input()
        d, k, values = _extract_parse_result(result)
        assert d == 1, f"Expected d=1, got {d}"
        assert k == 1, f"Expected k=1, got {k}"
        assert values == [(128, 50)], f"Unexpected values: {values}"

    def test_parse_input_boundary_r_values(self):
        """Parse input with boundary r values 0 and 255."""
        stdin_data = "2 1\n0 10\n255 20\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            result = parse_input()
        d, k, values = _extract_parse_result(result)
        assert values[0][0] == 0, f"Expected first r=0, got {values[0][0]}"
        assert values[1][0] == 255, f"Expected second r=255, got {values[1][0]}"

    def test_parse_input_postcondition_sorted(self):
        """Returned values are sorted in strictly increasing order of r."""
        stdin_data = "4 2\n5 1\n10 2\n20 3\n100 4\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            result = parse_input()
        d, k, values = _extract_parse_result(result)
        for i in range(len(values) - 1):
            assert values[i][0] < values[i + 1][0], \
                f"Values not strictly increasing at index {i}: {values[i][0]} >= {values[i+1][0]}"

    def test_parse_input_postcondition_d_equals_len(self):
        """Returned d equals the number of elements in returned values list."""
        stdin_data = "3 2\n1 10\n2 20\n3 30\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            result = parse_input()
        d, k, values = _extract_parse_result(result)
        assert d == len(values), f"d={d} but len(values)={len(values)}"

    def test_parse_input_error_empty_stdin(self):
        """Error when stdin is empty."""
        with patch('sys.stdin', io.StringIO("")):
            with pytest.raises(Exception):
                parse_input()

    def test_parse_input_error_malformed_tokens(self):
        """Error when tokens cannot be parsed as integers."""
        with patch('sys.stdin', io.StringIO("abc def\n")):
            with pytest.raises(Exception):
                parse_input()

    def test_parse_input_error_constraint_d_zero(self):
        """Error when d < 1."""
        with patch('sys.stdin', io.StringIO("0 0\n")):
            with pytest.raises(Exception):
                parse_input()

    def test_parse_input_error_constraint_k_gt_d(self):
        """Error when k > d."""
        with patch('sys.stdin', io.StringIO("2 3\n10 1\n20 1\n")):
            with pytest.raises(Exception):
                parse_input()

    def test_parse_input_error_constraint_r_out_of_range(self):
        """Error when r value exceeds 255."""
        with patch('sys.stdin', io.StringIO("1 1\n256 10\n")):
            with pytest.raises(Exception):
                parse_input()

    def test_parse_input_error_constraint_p_zero(self):
        """Error when p value is less than 1."""
        with patch('sys.stdin', io.StringIO("1 1\n10 0\n")):
            with pytest.raises(Exception):
                parse_input()


# ============================================================
# Tests for build_prefix_sums()
# ============================================================

class TestBuildPrefixSums:
    """Tests for build_prefix_sums function."""

    def test_build_prefix_sums_happy_basic(self):
        """Build prefix sums for 3 values and verify all arrays."""
        values = _make_values_arg([(10, 2), (20, 3), (30, 5)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert s0 == [0, 2, 5, 10], f"s0 mismatch: {s0}"
        assert s1 == [0, 20, 80, 230], f"s1 mismatch: {s1}"
        assert s2 == [0, 200, 1400, 5900], f"s2 mismatch: {s2}"

    def test_build_prefix_sums_happy_single(self):
        """Build prefix sums for a single value."""
        values = _make_values_arg([(100, 7)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert s0 == [0, 7], f"s0 mismatch: {s0}"
        assert s1 == [0, 700], f"s1 mismatch: {s1}"
        assert s2 == [0, 70000], f"s2 mismatch: {s2}"

    def test_build_prefix_sums_zero_r(self):
        """Build prefix sums when r=0."""
        values = _make_values_arg([(0, 5), (255, 3)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert s0 == [0, 5, 8], f"s0 mismatch: {s0}"
        assert s1 == [0, 0, 765], f"s1 mismatch: {s1}"
        assert s2 == [0, 0, 195075], f"s2 mismatch: {s2}"

    def test_build_prefix_sums_length_invariant(self):
        """Prefix sum arrays have length d+1."""
        values = _make_values_arg([(1, 1), (2, 2), (3, 3), (4, 4)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert len(s0) == 5, f"Expected len(s0)=5, got {len(s0)}"
        assert len(s1) == 5, f"Expected len(s1)=5, got {len(s1)}"
        assert len(s2) == 5, f"Expected len(s2)=5, got {len(s2)}"

    def test_build_prefix_sums_starts_zero(self):
        """All prefix sum arrays start with 0."""
        values = _make_values_arg([(50, 10), (100, 20)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert s0[0] == 0, f"s0[0] should be 0, got {s0[0]}"
        assert s1[0] == 0, f"s1[0] should be 0, got {s1[0]}"
        assert s2[0] == 0, f"s2[0] should be 0, got {s2[0]}"

    def test_build_prefix_sums_non_negative(self):
        """All prefix sum elements are non-negative integers."""
        values = _make_values_arg([(0, 1), (128, 5), (255, 3)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        assert all(x >= 0 for x in s0), f"s0 has negative elements: {s0}"
        assert all(x >= 0 for x in s1), f"s1 has negative elements: {s1}"
        assert all(x >= 0 for x in s2), f"s2 has negative elements: {s2}"

    def test_build_prefix_sums_non_decreasing(self):
        """s0 should be non-decreasing since all p >= 1."""
        values = _make_values_arg([(10, 3), (20, 1), (30, 7)])
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)
        for i in range(1, len(s0)):
            assert s0[i] >= s0[i - 1], f"s0 not non-decreasing at index {i}"

    def test_build_prefix_sums_error_empty(self):
        """Error when values list is empty."""
        with pytest.raises(Exception):
            build_prefix_sums([])


# ============================================================
# Tests for cost()
# ============================================================

class TestCost:
    """Tests for cost function."""

    def test_cost_single_element(self):
        """Cost of a single-element group equals 0."""
        s0, s1, s2 = _make_prefix_sums([(10, 5)])
        result = cost(0, 0, s0, s1, s2)
        assert result == 0, f"Single element cost should be 0, got {result}"

    def test_cost_two_equal_weights(self):
        """Cost of two-element group: values 0 and 10 with equal weights. Mean=5, SSE=50."""
        s0, s1, s2 = _make_prefix_sums([(0, 1), (10, 1)])
        result = cost(0, 1, s0, s1, s2)
        assert result == 50, f"Expected cost 50, got {result}"

    def test_cost_asymmetric_weights(self):
        """Cost with asymmetric weights: (0,1),(10,3). Mean=7.5. floor=7: 49+27=76. ceil=8: 64+12=76."""
        s0, s1, s2 = _make_prefix_sums([(0, 1), (10, 3)])
        result = cost(0, 1, s0, s1, s2)
        assert result == 76, f"Expected cost 76, got {result}"

    def test_cost_full_range_three_values(self):
        """Cost over 3 values: (0,1),(100,1),(200,1). Mean=100. SSE=20000."""
        s0, s1, s2 = _make_prefix_sums([(0, 1), (100, 1), (200, 1)])
        result = cost(0, 2, s0, s1, s2)
        assert result == 20000, f"Expected cost 20000, got {result}"

    def test_cost_partial_range(self):
        """Cost on a subrange: values (0,1),(10,1),(20,1),(30,1), group [1..2]=(10,20). Mean=15, SSE=50."""
        s0, s1, s2 = _make_prefix_sums([(0, 1), (10, 1), (20, 1), (30, 1)])
        result = cost(1, 2, s0, s1, s2)
        assert result == 50, f"Expected cost 50, got {result}"

    def test_cost_adjacent_values(self):
        """Cost of (254,1),(255,1). Mean=254.5. floor=254: 0+1=1. ceil=255: 1+0=1."""
        s0, s1, s2 = _make_prefix_sums([(254, 1), (255, 1)])
        result = cost(0, 1, s0, s1, s2)
        assert result == 1, f"Expected cost 1, got {result}"

    def test_cost_nonnegative(self):
        """Cost is always non-negative."""
        s0, s1, s2 = _make_prefix_sums([(5, 3), (50, 7), (200, 2)])
        for i in range(3):
            for j in range(i, 3):
                result = cost(i, j, s0, s1, s2)
                assert result >= 0, f"cost({i},{j}) returned negative: {result}"

    def test_cost_is_integer(self):
        """Cost returns a Python integer, not float."""
        s0, s1, s2 = _make_prefix_sums([(1, 3), (4, 7)])
        result = cost(0, 1, s0, s1, s2)
        assert isinstance(result, int), f"Expected int, got {type(result)}"

    def test_cost_zero_iff_same_values(self):
        """Cost is 0 if and only if all r values in group are the same."""
        # Single value => cost 0
        s0, s1, s2 = _make_prefix_sums([(42, 10)])
        assert cost(0, 0, s0, s1, s2) == 0

        # Two different values => cost > 0
        s0, s1, s2 = _make_prefix_sums([(42, 10), (43, 10)])
        assert cost(0, 1, s0, s1, s2) > 0

    def test_cost_weighted_mean_floor_ceil_difference(self):
        """Test where floor and ceil of mean give different SSE; verify minimum is returned."""
        # values: (0,1), (3,2). Total weight=3, weighted sum=6, mean=2.0 (exact integer).
        # SSE with v=2: 1*(0-2)^2 + 2*(3-2)^2 = 4 + 2 = 6
        s0, s1, s2 = _make_prefix_sums([(0, 1), (3, 2)])
        result = cost(0, 1, s0, s1, s2)
        assert result == 6, f"Expected cost 6, got {result}"

    def test_cost_error_i_greater_than_j(self):
        """Error when i > j."""
        s0, s1, s2 = _make_prefix_sums([(10, 1), (20, 1), (30, 1)])
        with pytest.raises(Exception):
            cost(2, 1, s0, s1, s2)

    def test_cost_error_negative_i(self):
        """Error when i < 0."""
        s0, s1, s2 = _make_prefix_sums([(10, 1), (20, 1)])
        with pytest.raises(Exception):
            cost(-1, 0, s0, s1, s2)

    def test_cost_error_j_too_large(self):
        """Error when j+1 >= len(s0), i.e., j exceeds valid range."""
        s0, s1, s2 = _make_prefix_sums([(10, 1), (20, 1)])
        # s0 has length 3, so j must be < 2. j=2 means j+1=3 >= 3.
        with pytest.raises(Exception):
            cost(0, 2, s0, s1, s2)


# ============================================================
# Tests for solve()
# ============================================================

class TestSolve:
    """Tests for solve function."""

    def test_solve_k_equals_d(self):
        """When k == d, answer is 0."""
        values = [(10, 1), (20, 1), (30, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(3, 3, s0, s1, s2)
        assert result == 0, f"Expected 0 when k==d, got {result}"

    def test_solve_k_greater_than_d(self):
        """When k > d, answer is still 0."""
        values = [(10, 1), (20, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(2, 5, s0, s1, s2)
        assert result == 0, f"Expected 0 when k>d, got {result}"

    def test_solve_k1_two_values(self):
        """k=1 means single representative. (0,1),(10,1) => cost 50."""
        values = [(0, 1), (10, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(2, 1, s0, s1, s2)
        assert result == 50, f"Expected 50, got {result}"

    def test_solve_single_value(self):
        """d=1 k=1 always yields 0."""
        values = [(128, 1000)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(1, 1, s0, s1, s2)
        assert result == 0, f"Expected 0 for single value, got {result}"

    def test_solve_k2_splits_reduce_cost(self):
        """k=2 can split (0,1),(1,1),(100,1) into {0,1} and {100}, reducing cost."""
        values = [(0, 1), (1, 1), (100, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        result_k1 = solve(3, 1, s0, s1, s2)
        result_k2 = solve(3, 2, s0, s1, s2)
        assert result_k2 <= result_k1, \
            f"k=2 cost ({result_k2}) should be <= k=1 cost ({result_k1})"
        # {0,1} has cost: mean~0.5, floor=0: 0+1=1, ceil=1: 1+0=1 => 1. {100}: 0. Total <= 1
        assert result_k2 <= 1, f"Expected cost <= 1 for k=2, got {result_k2}"

    def test_solve_monotonicity_in_k(self):
        """Increasing k should not increase the total SSE."""
        values = [(0, 1), (50, 1), (200, 1), (255, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        costs = [solve(4, k, s0, s1, s2) for k in range(1, 5)]
        for i in range(len(costs) - 1):
            assert costs[i] >= costs[i + 1], \
                f"Cost should be non-increasing in k: cost[k={i+1}]={costs[i]} < cost[k={i+2}]={costs[i+1]}"
        assert costs[-1] == 0, f"cost at k=d should be 0, got {costs[-1]}"

    def test_solve_nonnegative_integer(self):
        """Solve always returns a non-negative integer."""
        values = [(10, 5), (100, 3), (200, 7)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(3, 2, s0, s1, s2)
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert result >= 0, f"Expected non-negative, got {result}"

    def test_solve_contiguous_partition_known(self):
        """Known optimal: (0,1),(1,1),(100,1),(101,1) with k=2. Best: {0,1}+{100,101}. Cost<=2."""
        values = [(0, 1), (1, 1), (100, 1), (101, 1)]
        s0, s1, s2 = _make_prefix_sums(values)
        result = solve(4, 2, s0, s1, s2)
        # {0,1}: mean=0.5 => floor=0 cost=0+1=1 or ceil=1 cost=1+0=1 => 1
        # {100,101}: mean=100.5 => floor=100 cost=0+1=1 or ceil=101 cost=1+0=1 => 1
        # Total = 2
        assert result <= 2, f"Expected cost <= 2, got {result}"

    def test_solve_error_prefix_length_mismatch(self):
        """Error when prefix sum length doesn't match d+1."""
        s0 = [0, 1, 2]  # length 3, but d=3 expects length 4
        s1 = [0, 1, 2]
        s2 = [0, 1, 2]
        with pytest.raises(Exception):
            solve(3, 2, s0, s1, s2)

    def test_solve_error_invalid_d_zero(self):
        """Error when d < 1."""
        with pytest.raises(Exception):
            solve(0, 1, [0], [0], [0])

    def test_solve_error_invalid_k_zero(self):
        """Error when k < 1."""
        s0, s1, s2 = _make_prefix_sums([(10, 1), (20, 1), (30, 1)])
        with pytest.raises(Exception):
            solve(3, 0, s0, s1, s2)


# ============================================================
# Tests for main()
# ============================================================

class TestMain:
    """Tests for main function (end-to-end)."""

    def test_main_happy_basic(self):
        """End-to-end: main reads stdin, computes, prints a single integer line."""
        stdin_data = "3 2\n10 100\n20 200\n30 300\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            output = captured.getvalue().strip()
        assert output != "", "main() should print output"
        assert output.lstrip('-').isdigit(), f"Output should be integer, got '{output}'"
        val = int(output)
        assert val >= 0, f"Output should be non-negative, got {val}"

    def test_main_happy_trivial_single_value(self):
        """End-to-end: single value yields 0."""
        stdin_data = "1 1\n42 100\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            output = captured.getvalue().strip()
        assert output == "0", f"Expected '0', got '{output}'"

    def test_main_happy_k_equals_d(self):
        """End-to-end: k=d yields 0."""
        stdin_data = "2 2\n0 1\n255 1\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            output = captured.getvalue().strip()
        assert output == "0", f"Expected '0', got '{output}'"

    def test_main_happy_two_values_k1(self):
        """End-to-end: 2 values k=1 => exact SSE of 50."""
        stdin_data = "2 1\n0 1\n10 1\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            output = captured.getvalue().strip()
        assert output == "50", f"Expected '50', got '{output}'"

    def test_main_single_output_line(self):
        """Main prints exactly one line to stdout."""
        stdin_data = "3 1\n10 1\n20 1\n30 1\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            lines = captured.getvalue().strip().split('\n')
        assert len(lines) == 1, f"Expected exactly 1 output line, got {len(lines)}: {lines}"

    def test_main_error_empty_stdin(self):
        """Main raises error on empty stdin."""
        with patch('sys.stdin', io.StringIO("")):
            with pytest.raises(Exception):
                main()


# ============================================================
# Integration / cross-function invariant tests
# ============================================================

class TestIntegration:
    """Cross-function integration and invariant tests."""

    def test_build_then_cost_consistency(self):
        """build_prefix_sums output works correctly with cost function."""
        values = [(5, 2), (10, 3), (20, 5)]
        result = build_prefix_sums(values)
        s0, s1, s2 = _extract_prefix_sums(result)

        # Compare with manually computed prefix sums
        ms0, ms1, ms2 = _make_prefix_sums(values)
        assert s0 == ms0, f"s0 mismatch: {s0} vs {ms0}"
        assert s1 == ms1, f"s1 mismatch: {s1} vs {ms1}"
        assert s2 == ms2, f"s2 mismatch: {s2} vs {ms2}"

        # Cost should work with these
        c = cost(0, 2, s0, s1, s2)
        assert isinstance(c, int) and c >= 0

    def test_full_pipeline_consistency(self):
        """Full pipeline: parse -> build -> solve produces consistent result."""
        stdin_data = "4 2\n0 1\n1 1\n100 1\n101 1\n"
        with patch('sys.stdin', io.StringIO(stdin_data)):
            parsed = parse_input()
        d, k, values = _extract_parse_result(parsed)

        ps_result = build_prefix_sums(_make_values_arg(values))
        s0, s1, s2 = _extract_prefix_sums(ps_result)

        result = solve(d, k, s0, s1, s2)
        assert isinstance(result, int), "solve should return int"
        assert result >= 0, "solve should return non-negative"
        assert result <= 2, f"Known optimal for this input is <= 2, got {result}"

    def test_solve_matches_main_output(self):
        """solve() result matches what main() prints to stdout."""
        values_data = [(0, 1), (10, 1), (20, 1)]
        stdin_data = "3 2\n0 1\n10 1\n20 1\n"

        # Get solve result directly
        s0, s1, s2 = _make_prefix_sums(values_data)
        solve_result = solve(3, 2, s0, s1, s2)

        # Get main output
        with patch('sys.stdin', io.StringIO(stdin_data)):
            from io import StringIO
            captured = StringIO()
            with patch('sys.stdout', captured):
                main()
            main_output = int(captured.getvalue().strip())

        assert solve_result == main_output, \
            f"solve returned {solve_result} but main printed {main_output}"

    def test_integer_arithmetic_invariant(self):
        """All computations use integer arithmetic; no float contamination in cost."""
        values = [(1, 3), (4, 7), (9, 2)]
        s0, s1, s2 = _make_prefix_sums(values)
        for i in range(3):
            for j in range(i, 3):
                c = cost(i, j, s0, s1, s2)
                assert isinstance(c, int), \
                    f"cost({i},{j}) returned {type(c).__name__}, expected int"

    def test_larger_case_monotonicity(self):
        """Test monotonicity of solve for a larger case with 8 values."""
        import random
        random.seed(42)
        r_vals = sorted(random.sample(range(256), 8))
        values = [(r, random.randint(1, 100)) for r in r_vals]
        s0, s1, s2 = _make_prefix_sums(values)
        d = len(values)

        prev_cost = None
        for k in range(1, d + 1):
            c = solve(d, k, s0, s1, s2)
            assert c >= 0, f"Negative cost at k={k}"
            assert isinstance(c, int), f"Non-integer cost at k={k}"
            if prev_cost is not None:
                assert c <= prev_cost, \
                    f"Cost increased from k={k-1} ({prev_cost}) to k={k} ({c})"
            prev_cost = c
        # At k=d, cost should be 0
        assert solve(d, d, s0, s1, s2) == 0, "Cost at k=d should be 0"
