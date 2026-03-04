"""
Contract test suite for posterize_solution.
Covers build_prefix_sums, compute_cost, solve, and main.
Run with: pytest contract_test.py -v
"""

import sys
import io
import random
import itertools
import pytest
from unittest.mock import patch

# Import the module under test
from src.posterize_solution import (
    build_prefix_sums,
    compute_cost,
    solve,
    main,
)


# ============================================================
# Layer 1: Unit tests for build_prefix_sums
# ============================================================

class TestBuildPrefixSums:
    """Unit tests for build_prefix_sums."""

    def test_bps_happy_single(self):
        """build_prefix_sums with a single value produces correct prefix arrays of length 2."""
        result = build_prefix_sums(1, [10], [5])
        assert result.prefix_p == [0, 5], f"prefix_p mismatch: {result.prefix_p}"
        assert result.prefix_rp == [0, 50], f"prefix_rp mismatch: {result.prefix_rp}"
        assert result.prefix_r2p == [0, 500], f"prefix_r2p mismatch: {result.prefix_r2p}"

    def test_bps_happy_two(self):
        """build_prefix_sums with two values produces correct cumulative sums."""
        result = build_prefix_sums(2, [3, 7], [2, 4])
        assert result.prefix_p == [0, 2, 6], f"prefix_p mismatch: {result.prefix_p}"
        assert result.prefix_rp == [0, 6, 34], f"prefix_rp mismatch: {result.prefix_rp}"
        assert result.prefix_r2p == [0, 18, 214], f"prefix_r2p mismatch: {result.prefix_r2p}"

    def test_bps_happy_three_boundary_values(self):
        """build_prefix_sums with boundary values 0, 100, 255."""
        result = build_prefix_sums(3, [0, 100, 255], [1, 1, 1])
        assert result.prefix_p == [0, 1, 2, 3], f"prefix_p mismatch: {result.prefix_p}"
        assert result.prefix_rp == [0, 0, 100, 355], f"prefix_rp mismatch: {result.prefix_rp}"
        assert result.prefix_r2p == [0, 0, 10000, 75025], f"prefix_r2p mismatch: {result.prefix_r2p}"

    def test_bps_edge_length(self):
        """build_prefix_sums arrays always have length d+1."""
        result = build_prefix_sums(4, [1, 2, 3, 4], [10, 20, 30, 40])
        assert len(result.prefix_p) == 5, f"prefix_p length: {len(result.prefix_p)}"
        assert len(result.prefix_rp) == 5, f"prefix_rp length: {len(result.prefix_rp)}"
        assert len(result.prefix_r2p) == 5, f"prefix_r2p length: {len(result.prefix_r2p)}"

    def test_bps_edge_zero_index(self):
        """build_prefix_sums always has index 0 equal to 0 for all arrays."""
        result = build_prefix_sums(2, [50, 200], [100, 200])
        assert result.prefix_p[0] == 0, "prefix_p[0] should be 0"
        assert result.prefix_rp[0] == 0, "prefix_rp[0] should be 0"
        assert result.prefix_r2p[0] == 0, "prefix_r2p[0] should be 0"

    def test_bps_large_counts(self):
        """build_prefix_sums handles large counts correctly with integer arithmetic."""
        result = build_prefix_sums(2, [255, 128], [1000000, 1000000])
        assert result.prefix_p == [0, 1000000, 2000000], f"prefix_p: {result.prefix_p}"
        assert result.prefix_rp == [0, 255000000, 383000000], f"prefix_rp: {result.prefix_rp}"
        assert result.prefix_r2p == [0, 65025000000, 81409000000], f"prefix_r2p: {result.prefix_r2p}"

    def test_bps_recurrence_relation(self):
        """Verify prefix sum recurrence: prefix_p[i] = prefix_p[i-1] + counts[i-1]."""
        values = [5, 15, 25, 35, 45]
        counts = [3, 7, 11, 2, 9]
        d = 5
        result = build_prefix_sums(d, values, counts)
        for i in range(1, d + 1):
            assert result.prefix_p[i] == result.prefix_p[i - 1] + counts[i - 1], \
                f"prefix_p recurrence failed at i={i}"
            assert result.prefix_rp[i] == result.prefix_rp[i - 1] + values[i - 1] * counts[i - 1], \
                f"prefix_rp recurrence failed at i={i}"
            assert result.prefix_r2p[i] == result.prefix_r2p[i - 1] + values[i - 1] ** 2 * counts[i - 1], \
                f"prefix_r2p recurrence failed at i={i}"


# ============================================================
# Layer 1: Unit tests for compute_cost
# ============================================================

class TestComputeCost:
    """Unit tests for compute_cost."""

    def test_cc_single_element_returns_zero(self):
        """compute_cost for single element interval returns 0 (representative equals value)."""
        # value=10, count=5
        result = compute_cost(0, 0, [0, 5], [0, 50], [0, 500])
        assert result == 0, f"Single element cost should be 0, got {result}"

    def test_cc_single_element_value_zero(self):
        """compute_cost for single element with value 0 returns 0."""
        result = compute_cost(0, 0, [0, 100], [0, 0], [0, 0])
        assert result == 0, f"Expected 0, got {result}"

    def test_cc_single_element_value_255(self):
        """compute_cost for single element with value 255 returns 0."""
        # value=255, count=50: prefix_rp[1]=255*50=12750, prefix_r2p[1]=255^2*50=3251250
        result = compute_cost(0, 0, [0, 50], [0, 12750], [0, 3251250])
        assert result == 0, f"Expected 0, got {result}"

    def test_cc_two_elements_symmetric(self):
        """compute_cost for two-element interval: values=[0,10] counts=[1,1]. Mean=5, SSE=50."""
        result = compute_cost(0, 1, [0, 1, 2], [0, 0, 10], [0, 0, 100])
        assert result == 50, f"Expected 50, got {result}"

    def test_cc_weighted_floor_ceil_tie(self):
        """compute_cost with weighted counts where floor and ceil give same SSE."""
        # values=[0,10], counts=[1,3]. S=30, P=4, mean=7.5
        # v=7: 1*49+3*9=76; v=8: 1*64+3*4=76
        result = compute_cost(0, 1, [0, 1, 4], [0, 0, 30], [0, 0, 300])
        assert result == 76, f"Expected 76, got {result}"

    def test_cc_full_interval_nonneg(self):
        """compute_cost over full interval returns non-negative integer."""
        result = compute_cost(0, 2, [0, 1, 2, 3], [0, 0, 100, 355], [0, 0, 10000, 75025])
        assert result >= 0, f"Cost should be non-negative, got {result}"
        assert isinstance(result, int), f"Cost should be int, got {type(result)}"

    def test_cc_error_invalid_interval_a_gt_b(self):
        """compute_cost raises error when a > b."""
        with pytest.raises(Exception):
            compute_cost(2, 1, [0, 1, 2, 3], [0, 0, 100, 355], [0, 0, 10000, 75025])

    def test_cc_error_invalid_interval_b_ge_d(self):
        """compute_cost raises error when b >= d (prefix arrays have length d+1=4, so d=3, b=3 is invalid)."""
        with pytest.raises(Exception):
            compute_cost(0, 3, [0, 1, 2, 3], [0, 0, 100, 355], [0, 0, 10000, 75025])

    def test_cc_nonneg_invariant(self):
        """compute_cost always returns non-negative value."""
        # values=[50,100,150], counts=[10,20,30]
        pp = [0, 10, 30, 60]
        prp = [0, 500, 2500, 7000]
        pr2p = [0, 25000, 125000, 475000]
        # Recompute correct prefix sums:
        # prefix_rp: 0, 50*10=500, 500+100*20=2500, 2500+150*30=7000 ✓
        # prefix_r2p: 0, 2500*10=25000, 25000+10000*20=225000... wait
        # Actually: 50^2*10=25000, 100^2*20=200000, 150^2*30=675000
        # prefix_r2p = [0, 25000, 225000, 900000]
        pr2p_correct = [0, 25000, 225000, 900000]
        result = compute_cost(0, 2, pp, prp, pr2p_correct)
        assert result >= 0, f"Cost should be non-negative, got {result}"

    def test_cc_subinterval(self):
        """compute_cost on a subinterval (not starting at 0)."""
        # values=[0, 10, 20], counts=[1, 1, 1]
        # prefix_p = [0, 1, 2, 3]
        # prefix_rp = [0, 0, 10, 30]
        # prefix_r2p = [0, 0, 100, 500]
        # Interval [1, 2]: values 10, 20 counts 1,1. Mean=15, SSE=25+25=50
        result = compute_cost(1, 2, [0, 1, 2, 3], [0, 0, 10, 30], [0, 0, 100, 500])
        assert result == 50, f"Expected 50 for subinterval [1,2], got {result}"


# ============================================================
# Layer 2: Integration tests for solve
# ============================================================

class TestSolve:
    """Integration tests for solve."""

    def test_solve_d1_k1(self):
        """solve with d=1, k=1 returns 0."""
        result = solve(1, 1, [128], [100])
        assert result == 0, f"Expected 0, got {result}"

    def test_solve_k_eq_d(self):
        """solve with k=d returns 0 (each value maps to itself)."""
        result = solve(3, 3, [10, 50, 200], [5, 10, 3])
        assert result == 0, f"Expected 0, got {result}"

    def test_solve_k_gt_d(self):
        """solve with k>d returns 0."""
        result = solve(2, 5, [0, 255], [1, 1])
        assert result == 0, f"Expected 0, got {result}"

    def test_solve_d2_k1(self):
        """solve d=2 k=1: values=[0,10] counts=[1,1]. Mean=5, SSE=50."""
        result = solve(2, 1, [0, 10], [1, 1])
        assert result == 50, f"Expected 50, got {result}"

    def test_solve_d4_k2_two_clusters(self):
        """solve d=4 k=2: values=[0,1,100,101] counts=[1,1,1,1]. Optimal: split into {0,1} and {100,101}, cost=1+1=2."""
        result = solve(4, 2, [0, 1, 100, 101], [1, 1, 1, 1])
        assert result == 2, f"Expected 2, got {result}"

    def test_solve_d3_k2(self):
        """solve d=3 k=2: values=[0,1,255] counts=[1,1,1]."""
        result = solve(3, 2, [0, 1, 255], [1, 1, 1])
        # Best split: {0,1} rep 0 or 1 (cost 1) + {255} rep 255 (cost 0) = 1
        # Or {0} rep 0 + {1,255} with some rep. The first option gives cost 1.
        assert result >= 0, f"Expected non-negative, got {result}"
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        # The minimum should be 1 (group {0,1} with rep=0 cost=1, or rep=1 cost=1; group {255} cost=0)
        assert result <= 1, f"Expected at most 1, got {result}"

    def test_solve_d3_k1_full_range(self):
        """solve d=3 k=1: values=[0,100,255] counts=[1,1,1]. All mapped to single rep."""
        result = solve(3, 1, [0, 100, 255], [1, 1, 1])
        assert result >= 0
        assert isinstance(result, int)
        # Brute-force: try all v in [0, 255], pick min of sum((val-v)^2 for val in [0,100,255])
        min_sse = min(sum((val - v) ** 2 for val in [0, 100, 255]) for v in range(256))
        assert result == min_sse, f"Expected {min_sse}, got {result}"

    def test_solve_error_empty_values(self):
        """solve raises error when d>0 but values is empty."""
        with pytest.raises(Exception):
            solve(3, 2, [], [])

    def test_solve_error_mismatched_lengths(self):
        """solve raises error when len(values) != d."""
        with pytest.raises(Exception):
            solve(3, 2, [1, 2], [1, 2])

    def test_solve_nonnegative(self):
        """solve always returns a non-negative integer."""
        result = solve(3, 2, [0, 128, 255], [10, 20, 30])
        assert result >= 0, f"Expected non-negative, got {result}"
        assert isinstance(result, int), f"Expected int, got {type(result)}"

    def test_solve_exact_integer(self):
        """solve returns an exact integer, not a float."""
        result = solve(2, 1, [0, 255], [1, 1])
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert result >= 0

    def test_solve_monotonicity_in_k(self):
        """solve is monotonically non-increasing as k increases."""
        values = [10, 50, 100, 150, 200]
        counts = [3, 7, 2, 5, 4]
        d = 5
        results = [solve(d, k, values, counts) for k in range(1, d + 1)]
        for i in range(len(results) - 1):
            assert results[i] >= results[i + 1], \
                f"Monotonicity violated: solve(k={i + 1})={results[i]} < solve(k={i + 2})={results[i + 1]}"

    def test_solve_k_eq_d_always_zero(self):
        """For k >= d, the answer is always 0."""
        for d, values, counts in [
            (1, [0], [1]),
            (2, [0, 255], [100, 200]),
            (4, [10, 20, 30, 40], [1, 1, 1, 1]),
        ]:
            result = solve(d, d, values, counts)
            assert result == 0, f"Expected 0 for d=k={d}, got {result}"

    def test_solve_large_counts_integer_arithmetic(self):
        """solve handles large counts and produces exact integer results."""
        result = solve(3, 2, [1, 127, 254], [1000000, 1000000, 1000000])
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert result >= 0


# ============================================================
# Layer 3: End-to-end tests for main
# ============================================================

class TestMain:
    """End-to-end tests for main()."""

    def test_main_happy_simple(self):
        """main reads stdin and writes correct result for d=1 k=1."""
        input_data = "1 1\n128 100\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            captured = io.StringIO()
            with patch('sys.stdout', captured):
                main()
        output = captured.getvalue()
        assert output.strip() == '0', f"Expected '0', got '{output.strip()}'"

    def test_main_happy_format(self):
        """main output has no trailing spaces, ends with single newline."""
        input_data = "2 1\n0 1\n10 1\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            captured = io.StringIO()
            with patch('sys.stdout', captured):
                main()
        output = captured.getvalue()
        assert output == '50\n', f"Expected '50\\n', got {repr(output)}"

    def test_main_happy_k_eq_d(self):
        """main prints 0 when k equals d."""
        input_data = "3 3\n10 5\n50 10\n200 3\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            captured = io.StringIO()
            with patch('sys.stdout', captured):
                main()
        output = captured.getvalue()
        assert output.strip() == '0', f"Expected '0', got '{output.strip()}'"

    def test_main_d4_k2(self):
        """main with d=4, k=2, two clusters."""
        input_data = "4 2\n0 1\n1 1\n100 1\n101 1\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            captured = io.StringIO()
            with patch('sys.stdout', captured):
                main()
        output = captured.getvalue()
        assert output.strip() == '2', f"Expected '2', got '{output.strip()}'"

    def test_main_error_empty_input(self):
        """main raises error on empty stdin."""
        with patch('sys.stdin', io.StringIO("")):
            with pytest.raises(Exception):
                main()

    def test_main_error_malformed_input(self):
        """main raises error on malformed input (non-integer tokens)."""
        with patch('sys.stdin', io.StringIO("abc def\n")):
            with pytest.raises(Exception):
                main()


# ============================================================
# Layer 4: Stress / Property tests
# ============================================================

class TestStressAndProperties:
    """Stress tests and property-based tests using brute-force oracle."""

    @staticmethod
    def brute_force_solve(d, k, values, counts):
        """
        Brute-force oracle: try all ways to partition d sorted values into
        at most k contiguous groups, each with optimal integer representative.
        """
        if k >= d:
            return 0

        def cost_single_group(vals, cnts):
            """Min SSE for one group mapped to best integer in [0, 255]."""
            best = float('inf')
            # Compute weighted mean and try floor/ceil
            total_p = sum(cnts)
            if total_p == 0:
                return 0
            total_rp = sum(v * c for v, c in zip(vals, cnts))
            mean = total_rp / total_p
            candidates = set()
            candidates.add(max(0, min(255, int(mean))))
            candidates.add(max(0, min(255, int(mean) + 1)))
            for v in candidates:
                sse = sum(c * (val - v) ** 2 for val, c in zip(vals, cnts))
                best = min(best, sse)
            return best

        # DP approach matching the contract but brute-force computed costs
        INF = float('inf')
        # dp[m][i] = min SSE using m groups for first i values
        dp = [[INF] * (d + 1) for _ in range(k + 1)]
        for m in range(k + 1):
            dp[m][0] = 0

        for m in range(1, k + 1):
            for i in range(1, d + 1):
                for j in range(0, i):
                    # Group [j, i-1] (0-indexed into values)
                    group_vals = values[j:i]
                    group_cnts = counts[j:i]
                    c = cost_single_group(group_vals, group_cnts)
                    prev = dp[m - 1][j] if m >= 2 else (dp[0][j])
                    if prev + c < dp[m][i]:
                        dp[m][i] = prev + c

        return dp[k][d]

    def test_stress_brute_force(self):
        """Compare solve against brute-force oracle for small random inputs."""
        rng = random.Random(42)
        num_tests = 50
        for test_idx in range(num_tests):
            d = rng.randint(1, 6)
            k = rng.randint(1, d)
            all_vals = rng.sample(range(256), d)
            all_vals.sort()
            cnts = [rng.randint(1, 100) for _ in range(d)]

            expected = self.brute_force_solve(d, k, all_vals, cnts)
            actual = solve(d, k, all_vals, cnts)

            assert actual == expected, (
                f"Test {test_idx}: d={d}, k={k}, values={all_vals}, counts={cnts}: "
                f"expected {expected}, got {actual}"
            )

    def test_monotonicity_random(self):
        """For random inputs, verify solve(d, k, ...) >= solve(d, k+1, ...)."""
        rng = random.Random(123)
        for _ in range(20):
            d = rng.randint(2, 8)
            all_vals = sorted(rng.sample(range(256), d))
            cnts = [rng.randint(1, 50) for _ in range(d)]

            prev_result = None
            for k in range(1, d + 1):
                result = solve(d, k, all_vals, cnts)
                if prev_result is not None:
                    assert result <= prev_result, (
                        f"Monotonicity violated: d={d}, values={all_vals}, counts={cnts}, "
                        f"solve(k={k - 1})={prev_result}, solve(k={k})={result}"
                    )
                prev_result = result

            # k=d should give 0
            assert solve(d, d, all_vals, cnts) == 0, (
                f"k=d should give 0: d={d}, values={all_vals}, counts={cnts}"
            )

    def test_large_counts_stress(self):
        """Exercise big-integer arithmetic paths with large pixel counts."""
        values = [0, 128, 255]
        counts = [10**9, 10**9, 10**9]
        d = 3
        k = 2
        result = solve(d, k, values, counts)
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert result >= 0, f"Expected non-negative, got {result}"
        # With k=2, best split: {0, 128} or {128, 255} or {0} and {128, 255}
        # Verify k=3 gives 0
        assert solve(d, 3, values, counts) == 0

    def test_all_same_values_adjacent(self):
        """When all values are consecutive integers, verify correct behavior."""
        d = 5
        values = [10, 11, 12, 13, 14]
        counts = [1, 1, 1, 1, 1]
        # k=1: mean=12, SSE = (10-12)^2+(11-12)^2+(12-12)^2+(13-12)^2+(14-12)^2 = 4+1+0+1+4=10
        result = solve(d, 1, values, counts)
        assert result == 10, f"Expected 10, got {result}"
        # k=2: e.g. {10,11} rep=10 or 11 cost=1, {12,13,14} rep=13 cost=2 => total=3
        #   or {10,11,12} rep=11 cost=2, {13,14} rep=13 or 14 cost=1 => total=3
        result_k2 = solve(d, 2, values, counts)
        assert result_k2 <= 10, f"k=2 should be <= k=1 result"
        assert result_k2 >= 0

    def test_single_value_large_count(self):
        """Single value with very large count gives 0."""
        result = solve(1, 1, [127], [10**15])
        assert result == 0, f"Expected 0, got {result}"

    def test_two_extreme_values(self):
        """Two extreme values (0 and 255) with k=1."""
        result = solve(2, 1, [0, 255], [1, 1])
        # Mean = 127.5, try v=127: 127^2 + 128^2 = 16129 + 16384 = 32513
        # try v=128: 128^2 + 127^2 = same = 32513
        assert result == 32513, f"Expected 32513, got {result}"


# ============================================================
# Additional invariant tests
# ============================================================

class TestInvariants:
    """Tests for contract invariants."""

    def test_dp_base_zero_via_solve(self):
        """DP base case: dp[m][0]==0 verified via solve returning 0 when k>=d."""
        assert solve(4, 4, [10, 20, 30, 40], [1, 1, 1, 1]) == 0

    def test_single_rep_base_case(self):
        """dp[1][i] == compute_cost(0, i-1): verify solve with k=1 matches compute_cost over full range."""
        values = [0, 100, 255]
        counts = [1, 1, 1]
        d = 3
        ps = build_prefix_sums(d, values, counts)
        cc = compute_cost(0, d - 1, ps.prefix_p, ps.prefix_rp, ps.prefix_r2p)
        sv = solve(d, 1, values, counts)
        assert sv == cc, f"solve(k=1)={sv} should equal compute_cost(0,{d - 1})={cc}"

    def test_compute_cost_consistency_with_prefix_sums(self):
        """Verify compute_cost uses prefix sums from build_prefix_sums correctly."""
        values = [10, 20, 30]
        counts = [5, 3, 7]
        d = 3
        ps = build_prefix_sums(d, values, counts)

        # Single elements should be 0
        for i in range(d):
            c = compute_cost(i, i, ps.prefix_p, ps.prefix_rp, ps.prefix_r2p)
            assert c == 0, f"Single element cost at index {i} should be 0, got {c}"

    def test_more_values_never_increases_sse(self):
        """dp[m][i] <= dp[m-1][i]: more allowed values never increases the minimum SSE."""
        values = [0, 50, 100, 150, 200, 250]
        counts = [10, 20, 30, 40, 50, 60]
        d = 6
        results = [solve(d, k, values, counts) for k in range(1, d + 1)]
        for i in range(len(results) - 1):
            assert results[i] >= results[i + 1], \
                f"More values should not increase SSE: k={i + 1} gave {results[i]}, k={i + 2} gave {results[i + 1]}"

    def test_final_answer_nonneg_integer(self):
        """The final answer dp[k][d] is a non-negative integer."""
        result = solve(5, 3, [10, 50, 100, 150, 200], [1, 2, 3, 4, 5])
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert result >= 0, f"Expected non-negative, got {result}"
