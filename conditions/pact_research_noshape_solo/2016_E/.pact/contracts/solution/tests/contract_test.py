"""
Contract test suite for the Forever Young Solution.
Tests verify behavior at boundaries (inputs/outputs), not internals.
Covers happy paths, edge cases, error cases, and invariants.
"""
import pytest
import sys
import io
from unittest.mock import patch
from src.solution import (
    main,
    solve,
    to_base,
    reinterpret_base10,
    integer_kth_root,
    solve_phase1_two_digit,
    solve_phase2_three_digit,
    solve_phase3_four_plus_digit,
)


# ============================================================================
# Helper: brute-force oracle for small inputs
# ============================================================================
def brute_force_solve(y, l):
    """
    Brute-force oracle: try all bases from y down to 10, return the largest
    valid base b where y in base b has all digits in [0,9] and the base-10
    reinterpretation is >= l.
    """
    for b in range(y, 9, -1):
        digits = []
        n = y
        valid = True
        if n == 0:
            digits = [0]
        else:
            while n > 0:
                d = n % b
                if d >= 10:
                    valid = False
                    break
                digits.append(d)
                n //= b
            digits.reverse()
        if valid and digits:
            val = 0
            for d in digits:
                val = val * 10 + d
            if val >= l:
                return b
    return 10  # base 10 always works


# ============================================================================
# Tests for to_base
# ============================================================================
class TestToBase:
    """Unit tests for to_base function."""

    def test_to_base_happy_simple(self):
        """to_base converts 123 in base 10 to [1, 2, 3]"""
        result = to_base(123, 10)
        assert result == [1, 2, 3], f"Expected [1, 2, 3], got {result}"

    def test_to_base_happy_base2(self):
        """to_base converts 10 in base 2 to [1, 0, 1, 0]"""
        result = to_base(10, 2)
        assert result == [1, 0, 1, 0], f"Expected [1, 0, 1, 0], got {result}"

    def test_to_base_zero(self):
        """to_base converts 0 to [0] in any base"""
        result = to_base(0, 10)
        assert result == [0], f"Expected [0], got {result}"

    def test_to_base_zero_various_bases(self):
        """to_base converts 0 to [0] in various bases"""
        for b in [2, 5, 10, 16, 100]:
            result = to_base(0, b)
            assert result == [0], f"Expected [0] for base {b}, got {result}"

    def test_to_base_base11_valid(self):
        """to_base(11, 11) should return [1, 0] since 11 = 1*11 + 0"""
        result = to_base(11, 11)
        assert result == [1, 0], f"Expected [1, 0], got {result}"

    def test_to_base_returns_none_for_digit_ge_10(self):
        """to_base returns None when a digit >= 10 (255 in base 16 has digits 15)"""
        result = to_base(255, 16)
        assert result is None, f"Expected None, got {result}"

    def test_to_base_returns_none_for_10_in_base_10_NOT(self):
        """to_base(10, 10) should be [1, 0], all valid"""
        result = to_base(10, 10)
        assert result == [1, 0], f"Expected [1, 0], got {result}"

    def test_to_base_single_digit(self):
        """to_base of single digit returns list with one element"""
        result = to_base(9, 10)
        assert result == [9], f"Expected [9], got {result}"

    def test_to_base_single_digit_in_large_base(self):
        """to_base(5, 100) returns [5]"""
        result = to_base(5, 100)
        assert result == [5], f"Expected [5], got {result}"

    def test_to_base_large_number(self):
        """to_base handles y = 10^18 in base 10"""
        result = to_base(1000000000000000000, 10)
        assert result is not None, "Expected non-None result"
        assert result[0] == 1, f"Expected leading digit 1, got {result[0]}"
        assert all(d == 0 for d in result[1:]), "Expected all trailing zeros"
        assert len(result) == 19, f"Expected 19 digits, got {len(result)}"

    def test_to_base_base11_14641(self):
        """to_base correctly converts 14641 (11^4) to base 11"""
        result = to_base(14641, 11)
        assert result == [1, 0, 0, 0, 0], f"Expected [1, 0, 0, 0, 0], got {result}"

    def test_to_base_reconstruction_property(self):
        """to_base result reconstructs to original number"""
        y, b = 9876, 10
        result = to_base(y, b)
        assert result is not None, "Expected non-None result"
        reconstructed = sum(d * b ** (len(result) - 1 - i) for i, d in enumerate(result))
        assert reconstructed == y, f"Reconstruction {reconstructed} != {y}"

    def test_to_base_reconstruction_property_various_bases(self):
        """to_base reconstruction works for various bases"""
        for y in [1, 42, 100, 999, 12345]:
            for b in [10, 11, 12, 20, 100]:
                result = to_base(y, b)
                if result is not None:
                    reconstructed = sum(
                        d * b ** (len(result) - 1 - i)
                        for i, d in enumerate(result)
                    )
                    assert reconstructed == y, (
                        f"Reconstruction failed for y={y}, b={b}: "
                        f"got {reconstructed}"
                    )

    def test_to_base_no_leading_zeros(self):
        """to_base result has no leading zeros for y > 0"""
        for y in [1, 10, 100, 999, 12345]:
            for b in [10, 11, 16]:
                result = to_base(y, b)
                if result is not None:
                    assert result[0] != 0, (
                        f"Leading zero found for y={y}, b={b}: {result}"
                    )

    def test_to_base_all_digits_valid_range(self):
        """When to_base returns non-None, all digits are in [0, 9]"""
        for y in [1, 42, 100, 999, 12345]:
            for b in [10, 11, 20, 100]:
                result = to_base(y, b)
                if result is not None:
                    for d in result:
                        assert 0 <= d <= 9, (
                            f"Digit {d} out of range for y={y}, b={b}"
                        )

    def test_to_base_invalid_base_error(self):
        """to_base raises error when b < 2"""
        with pytest.raises(Exception):
            to_base(10, 1)

    def test_to_base_invalid_base_zero(self):
        """to_base raises error when b = 0"""
        with pytest.raises(Exception):
            to_base(10, 0)

    def test_to_base_negative_input_error(self):
        """to_base raises error when y < 0"""
        with pytest.raises(Exception):
            to_base(-1, 10)


# ============================================================================
# Tests for reinterpret_base10
# ============================================================================
class TestReinterpretBase10:
    """Unit tests for reinterpret_base10 function."""

    def test_reinterpret_happy(self):
        """reinterpret_base10 interprets [1, 2, 3] as 123"""
        result = reinterpret_base10([1, 2, 3])
        assert result == 123, f"Expected 123, got {result}"

    def test_reinterpret_single_digit(self):
        """reinterpret_base10 interprets [5] as 5"""
        result = reinterpret_base10([5])
        assert result == 5, f"Expected 5, got {result}"

    def test_reinterpret_zero(self):
        """reinterpret_base10 of [0] returns 0"""
        result = reinterpret_base10([0])
        assert result == 0, f"Expected 0, got {result}"

    def test_reinterpret_leading_zero(self):
        """reinterpret_base10 of [0, 1] returns 1"""
        result = reinterpret_base10([0, 1])
        assert result == 1, f"Expected 1, got {result}"

    def test_reinterpret_large_digits(self):
        """reinterpret_base10 handles a 19-digit number (10^18)"""
        digits = [1] + [0] * 18
        result = reinterpret_base10(digits)
        assert result == 1000000000000000000, f"Expected 10^18, got {result}"

    def test_reinterpret_all_nines(self):
        """reinterpret_base10 of [9, 9, 9] returns 999"""
        result = reinterpret_base10([9, 9, 9])
        assert result == 999, f"Expected 999, got {result}"

    def test_reinterpret_formula_property(self):
        """reinterpret_base10 follows the sum formula"""
        digits = [3, 1, 4, 1, 5]
        result = reinterpret_base10(digits)
        expected = sum(d * 10 ** (len(digits) - 1 - i) for i, d in enumerate(digits))
        assert result == expected, f"Expected {expected}, got {result}"

    def test_reinterpret_non_negative(self):
        """reinterpret_base10 always returns non-negative value"""
        for digits in [[0], [0, 0], [1], [9, 9, 9]]:
            result = reinterpret_base10(digits)
            assert result >= 0, f"Expected non-negative, got {result} for {digits}"

    def test_reinterpret_empty_error(self):
        """reinterpret_base10 raises error on empty list"""
        with pytest.raises(Exception):
            reinterpret_base10([])

    def test_reinterpret_digit_out_of_range_high(self):
        """reinterpret_base10 raises error when digit >= 10"""
        with pytest.raises(Exception):
            reinterpret_base10([1, 10, 3])

    def test_reinterpret_digit_out_of_range_negative(self):
        """reinterpret_base10 raises error when digit is negative"""
        with pytest.raises(Exception):
            reinterpret_base10([-1, 2])


# ============================================================================
# Tests for integer_kth_root
# ============================================================================
class TestIntegerKthRoot:
    """Unit tests for integer_kth_root function."""

    def test_ikr_square_root_exact(self):
        """integer_kth_root(100, 2) returns 10"""
        result = integer_kth_root(100, 2)
        assert result == 10, f"Expected 10, got {result}"

    def test_ikr_cube_root_exact(self):
        """integer_kth_root(27, 3) returns 3"""
        result = integer_kth_root(27, 3)
        assert result == 3, f"Expected 3, got {result}"

    def test_ikr_non_exact_sqrt(self):
        """integer_kth_root(10, 2) returns 3"""
        result = integer_kth_root(10, 2)
        assert result == 3, f"Expected 3, got {result}"

    def test_ikr_zero(self):
        """integer_kth_root(0, 5) returns 0"""
        result = integer_kth_root(0, 5)
        assert result == 0, f"Expected 0, got {result}"

    def test_ikr_one(self):
        """integer_kth_root(1, 1) returns 1"""
        result = integer_kth_root(1, 1)
        assert result == 1, f"Expected 1, got {result}"

    def test_ikr_k_equals_1(self):
        """integer_kth_root(n, 1) returns n"""
        result = integer_kth_root(999, 1)
        assert result == 999, f"Expected 999, got {result}"

    def test_ikr_large_sqrt(self):
        """integer_kth_root(10^18, 2) returns 10^9"""
        result = integer_kth_root(10**18, 2)
        assert result == 10**9, f"Expected 10^9, got {result}"

    def test_ikr_large_cube_root(self):
        """integer_kth_root(10^18, 3) returns 10^6"""
        result = integer_kth_root(10**18, 3)
        assert result == 10**6, f"Expected 10^6, got {result}"

    def test_ikr_4th_root(self):
        """integer_kth_root(10^18, 4) returns floor(10^4.5) = 31622"""
        result = integer_kth_root(10**18, 4)
        assert result**4 <= 10**18, f"r^4 > n: {result}^4 = {result**4}"
        assert (result + 1) ** 4 > 10**18, f"(r+1)^4 <= n"

    def test_ikr_postcondition_property(self):
        """integer_kth_root satisfies r^k <= n < (r+1)^k"""
        result = integer_kth_root(123456789, 4)
        assert result**4 <= 123456789, f"r^k > n"
        assert (result + 1) ** 4 > 123456789, f"(r+1)^k <= n"

    def test_ikr_postcondition_various(self):
        """Postcondition holds for various inputs"""
        test_cases = [
            (0, 2), (1, 2), (2, 2), (3, 3), (1000, 3),
            (10**9, 2), (10**12, 4), (10**18, 6),
        ]
        for n, k in test_cases:
            r = integer_kth_root(n, k)
            assert r >= 0, f"r < 0 for n={n}, k={k}"
            assert r**k <= n, f"r^k > n for n={n}, k={k}: {r}^{k} = {r**k}"
            assert (r + 1) ** k > n, (
                f"(r+1)^k <= n for n={n}, k={k}: {r+1}^{k} = {(r+1)**k}"
            )

    def test_ikr_powers_of_two(self):
        """integer_kth_root is exact for perfect powers"""
        assert integer_kth_root(256, 8) == 2
        assert integer_kth_root(1024, 10) == 2
        assert integer_kth_root(65536, 4) == 16

    def test_ikr_just_below_perfect_power(self):
        """integer_kth_root of n just below perfect power returns one less"""
        # 10^2 = 100, so floor(sqrt(99)) = 9
        result = integer_kth_root(99, 2)
        assert result == 9, f"Expected 9, got {result}"

    def test_ikr_negative_n_error(self):
        """integer_kth_root raises error for negative n"""
        with pytest.raises(Exception):
            integer_kth_root(-1, 2)

    def test_ikr_invalid_k_error(self):
        """integer_kth_root raises error for k < 1"""
        with pytest.raises(Exception):
            integer_kth_root(10, 0)

    def test_ikr_invalid_k_negative(self):
        """integer_kth_root raises error for negative k"""
        with pytest.raises(Exception):
            integer_kth_root(10, -1)


# ============================================================================
# Tests for solve_phase1_two_digit
# ============================================================================
class TestSolvePhase1TwoDigit:
    """Unit tests for solve_phase1_two_digit function."""

    def test_phase1_happy_large_base(self):
        """Phase 1: y=100, l=2. a=1,c=0 -> b=100, digits [1,0] -> 10>=2. Max base = 100."""
        result = solve_phase1_two_digit(100, 2)
        assert result == 100, f"Expected 100, got {result}"

    def test_phase1_happy_21_l2(self):
        """Phase 1: y=21, l=2. a=1,c=0 -> b=21. a=2,c=1 -> b=10 (not >=11). a=1,c=1 -> b=20. Max = 21."""
        result = solve_phase1_two_digit(21, 2)
        assert result == 21, f"Expected 21, got {result}"

    def test_phase1_returns_zero_for_small_y(self):
        """Phase 1: y=10, l=2. Only 2-digit base rep: base 10 -> [1,0]. Need b>=11. For a=1,c=0 -> b=10 (not >=11). No valid."""
        result = solve_phase1_two_digit(10, 2)
        assert result == 0, f"Expected 0, got {result}"

    def test_phase1_result_constraint_zero_or_ge_11(self):
        """Phase 1 returns 0 or a value >= 11"""
        for y in [10, 20, 50, 100, 200, 999]:
            for l_val in [2, 10, 50]:
                if l_val <= y:
                    result = solve_phase1_two_digit(y, l_val)
                    assert result == 0 or result >= 11, (
                        f"Phase 1 returned {result} for y={y}, l={l_val}"
                    )

    def test_phase1_l_constraint_filters(self):
        """Phase 1: high l filters out bases where reinterpretation < l"""
        # y=91, l=90. a=9,c=1 -> b=10 (not >= 11). a=1,c=0 -> b=91, digits [1,0] -> 10 < 90. 
        # a=7,c=0 -> b=13, digits [7,0] -> 70 < 90. a=9,c=1 -> b=10.
        result = solve_phase1_two_digit(91, 90)
        # Only (a,c) pairs where 10a+c >= 90: a=9,c>=0. 10*9+c >= 90 for any c.
        # a=9: b = (91-c)/9. c=1 -> b=10 (not >=11). c=0 -> b=91/9 not int.
        # So result should be 0
        assert result == 0 or result >= 11, f"Unexpected result {result}"

    def test_phase1_valid_result_satisfies_postcondition(self):
        """When Phase 1 returns b > 0, verify y = a*b + c with valid digits"""
        y, l_val = 100, 2
        result = solve_phase1_two_digit(y, l_val)
        if result > 0:
            digits = to_base(y, result)
            assert digits is not None, "Digits should not be None for valid base"
            assert len(digits) == 2, f"Expected 2 digits, got {len(digits)}"
            assert all(0 <= d <= 9 for d in digits), "All digits should be in [0,9]"
            val = reinterpret_base10(digits)
            assert val >= l_val, f"Reinterpreted value {val} < l={l_val}"


# ============================================================================
# Tests for solve_phase2_three_digit
# ============================================================================
class TestSolvePhase2ThreeDigit:
    """Unit tests for solve_phase2_three_digit function."""

    def test_phase2_happy_path(self):
        """Phase 2: y=1000, l=2. Looking for 3-digit bases."""
        result = solve_phase2_three_digit(1000, 2)
        assert result == 0 or result >= 11, f"Unexpected result {result}"

    def test_phase2_known_value(self):
        """Phase 2: y=133, base 11 -> 1*121+1*11+1=133 -> [1,1,1] -> 111>=2"""
        result = solve_phase2_three_digit(133, 2)
        if result > 0:
            assert result >= 11, f"Expected >= 11, got {result}"
            digits = to_base(133, result)
            assert digits is not None
            assert len(digits) == 3

    def test_phase2_no_valid_base_small_y(self):
        """Phase 2: y=10, l=2. No 3-digit representation possible in base >= 11"""
        result = solve_phase2_three_digit(10, 2)
        assert result == 0, f"Expected 0 for y=10, got {result}"

    def test_phase2_result_constraint(self):
        """Phase 2 returns 0 or >= 11"""
        for y in [100, 500, 1000, 5000]:
            result = solve_phase2_three_digit(y, 2)
            assert result == 0 or result >= 11, (
                f"Phase 2 returned {result} for y={y}"
            )

    def test_phase2_valid_result_satisfies_postcondition(self):
        """When Phase 2 returns b > 0, verify 3-digit representation"""
        # y = 1*11^2 + 2*11 + 3 = 121 + 22 + 3 = 146
        y = 146
        result = solve_phase2_three_digit(y, 2)
        if result > 0:
            digits = to_base(y, result)
            assert digits is not None
            assert len(digits) == 3
            assert all(0 <= d <= 9 for d in digits)
            val = reinterpret_base10(digits)
            assert val >= 2


# ============================================================================
# Tests for solve_phase3_four_plus_digit
# ============================================================================
class TestSolvePhase3FourPlusDigit:
    """Unit tests for solve_phase3_four_plus_digit function."""

    def test_phase3_happy_path(self):
        """Phase 3: y=14641=11^4, base 11 -> [1,0,0,0,0] (5 digits) -> 10000>=2"""
        result = solve_phase3_four_plus_digit(14641, 2)
        # Base 11 gives 5 digits (>= 4), should be found
        if result > 0:
            assert result >= 11, f"Expected >= 11, got {result}"
            digits = to_base(14641, result)
            assert digits is not None
            assert len(digits) >= 4

    def test_phase3_no_valid_base_small_y(self):
        """Phase 3: y=100, l=2. No 4-digit rep in base >= 11 possible."""
        result = solve_phase3_four_plus_digit(100, 2)
        assert result == 0, f"Expected 0 for y=100, got {result}"

    def test_phase3_result_constraint(self):
        """Phase 3 returns 0 or >= 11"""
        for y in [100, 1000, 10000, 100000]:
            result = solve_phase3_four_plus_digit(y, 2)
            assert result == 0 or result >= 11, (
                f"Phase 3 returned {result} for y={y}"
            )

    def test_phase3_valid_result_has_4_plus_digits(self):
        """When Phase 3 returns b > 0, representation has >= 4 digits"""
        y = 14641
        result = solve_phase3_four_plus_digit(y, 2)
        if result > 0:
            digits = to_base(y, result)
            assert digits is not None
            assert len(digits) >= 4, f"Expected >= 4 digits, got {len(digits)}"


# ============================================================================
# Tests for solve
# ============================================================================
class TestSolve:
    """Unit tests for the core solve function."""

    def test_solve_returns_at_least_10(self):
        """solve always returns base >= 10 (invariant: base 10 always valid)"""
        result = solve(100, 2)
        assert result >= 10, f"Expected >= 10, got {result}"

    def test_solve_y_equals_l(self):
        """solve when y == l: base 10 works (y in base 10 is y >= l)"""
        result = solve(100, 100)
        assert result >= 10, f"Expected >= 10, got {result}"

    def test_solve_minimum_inputs(self):
        """solve(2, 2): smallest valid input. Base 10 gives '2' >= 2. Answer is 10."""
        result = solve(2, 2)
        assert result == 10, f"Expected 10, got {result}"

    def test_solve_21_2(self):
        """solve(21, 2): base 21 gives [1,0] -> 10 >= 2. This should be max."""
        result = solve(21, 2)
        assert result == 21, f"Expected 21, got {result}"

    def test_solve_optimality(self):
        """solve returns the LARGEST valid base"""
        y, l_val = 21, 2
        result = solve(y, l_val)
        # Verify no larger base works
        for b in range(result + 1, y + 2):
            digits = to_base(y, b)
            if digits is not None:
                val = reinterpret_base10(digits)
                assert val < l_val, (
                    f"Base {b} > {result} is also valid with value {val} >= {l_val}"
                )

    def test_solve_validity_postconditions(self):
        """solve result satisfies all postconditions"""
        y, l_val = 500, 10
        result = solve(y, l_val)
        assert result >= 10, f"Base {result} < 10"
        digits = to_base(y, result)
        assert digits is not None, f"to_base({y}, {result}) returned None"
        val = reinterpret_base10(digits)
        assert val >= l_val, f"Reinterpreted value {val} < l={l_val}"

    def test_solve_validity_postconditions_various(self):
        """solve postconditions hold for various inputs"""
        test_cases = [
            (10, 2), (20, 5), (100, 10), (999, 50),
            (1000, 100), (12345, 2), (99999, 9999),
        ]
        for y, l_val in test_cases:
            result = solve(y, l_val)
            assert result >= 10, f"solve({y},{l_val}) returned {result} < 10"
            digits = to_base(y, result)
            assert digits is not None, f"to_base({y},{result}) returned None"
            val = reinterpret_base10(digits)
            assert val >= l_val, (
                f"solve({y},{l_val}): reinterpreted value {val} < {l_val} "
                f"for base {result}"
            )

    def test_solve_large_y(self):
        """solve handles y = 10^18"""
        result = solve(10**18, 2)
        assert result >= 10, f"Expected >= 10, got {result}"
        digits = to_base(10**18, result)
        assert digits is not None
        val = reinterpret_base10(digits)
        assert val >= 2

    def test_solve_large_y_l_equal(self):
        """solve handles y = l = 10^18"""
        result = solve(10**18, 10**18)
        assert result >= 10, f"Expected >= 10, got {result}"
        # Must be base 10 since y in base 10 is y itself = l
        assert result == 10, f"Expected 10 when y=l=10^18, got {result}"

    def test_solve_constraint_violation_y_lt_l(self):
        """solve raises error when y < l"""
        with pytest.raises(Exception):
            solve(5, 10)

    def test_solve_constraint_violation_l_lt_2(self):
        """solve raises error when l < 2"""
        with pytest.raises(Exception):
            solve(10, 1)

    def test_solve_constraint_violation_l_zero(self):
        """solve raises error when l = 0"""
        with pytest.raises(Exception):
            solve(10, 0)

    def test_solve_constraint_violation_negative(self):
        """solve raises error for negative inputs"""
        with pytest.raises(Exception):
            solve(-1, -2)

    def test_solve_base_10_always_valid_invariant(self):
        """Invariant: base 10 is always valid, so solve >= 10"""
        import random
        random.seed(42)
        for _ in range(20):
            y = random.randint(2, 10**6)
            l_val = random.randint(2, y)
            result = solve(y, l_val)
            assert result >= 10, (
                f"solve({y},{l_val}) returned {result} < 10"
            )

    def test_solve_result_bounded_by_y(self):
        """Invariant: result base <= y"""
        test_cases = [(10, 2), (100, 5), (1000, 10), (50, 3)]
        for y, l_val in test_cases:
            result = solve(y, l_val)
            assert result <= y, f"solve({y},{l_val}) = {result} > y={y}"


# ============================================================================
# Oracle / brute-force comparison tests
# ============================================================================
class TestSolveBruteForceOracle:
    """Compare solve against brute-force oracle for small inputs."""

    def test_oracle_small_range_l2(self):
        """Brute-force comparison for y in [10, 200], l=2"""
        for y in range(10, 201):
            expected = brute_force_solve(y, 2)
            result = solve(y, 2)
            assert result == expected, (
                f"solve({y}, 2) = {result}, oracle says {expected}"
            )

    def test_oracle_small_range_l10(self):
        """Brute-force comparison for y in [10, 200], l=10"""
        for y in range(10, 201):
            expected = brute_force_solve(y, 10)
            result = solve(y, 10)
            assert result == expected, (
                f"solve({y}, 10) = {result}, oracle says {expected}"
            )

    def test_oracle_y_equals_l_range(self):
        """Brute-force comparison for y == l in [2, 100]"""
        for y in range(2, 101):
            expected = brute_force_solve(y, y)
            result = solve(y, y)
            assert result == expected, (
                f"solve({y}, {y}) = {result}, oracle says {expected}"
            )

    def test_oracle_various_l_values(self):
        """Brute-force comparison for various (y, l) pairs"""
        import random
        random.seed(123)
        for _ in range(100):
            y = random.randint(2, 500)
            l_val = random.randint(2, y)
            expected = brute_force_solve(y, l_val)
            result = solve(y, l_val)
            assert result == expected, (
                f"solve({y}, {l_val}) = {result}, oracle says {expected}"
            )

    def test_oracle_medium_range(self):
        """Brute-force comparison for y in [200, 1000], l=2"""
        for y in range(200, 1001, 10):
            expected = brute_force_solve(y, 2)
            result = solve(y, 2)
            assert result == expected, (
                f"solve({y}, 2) = {result}, oracle says {expected}"
            )


# ============================================================================
# Tests for main (I/O integration)
# ============================================================================
class TestMain:
    """Integration tests for main() using mocked stdin/stdout."""

    def test_main_happy_path(self):
        """main reads '21 2' and prints result followed by newline"""
        with patch('sys.stdin', io.StringIO('21 2\n')):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                main()
                output = mock_out.getvalue()
                assert output.strip().isdigit() or (
                    output.strip().lstrip('-').isdigit()
                ), f"Output should be integer, got: {output!r}"
                assert output.endswith('\n'), "Output should end with newline"

    def test_main_output_matches_solve(self):
        """main output matches solve(21, 2)"""
        expected = solve(21, 2)
        with patch('sys.stdin', io.StringIO('21 2\n')):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                main()
                output = mock_out.getvalue().strip()
                assert int(output) == expected, (
                    f"Expected {expected}, got {output}"
                )

    def test_main_output_format_single_integer(self):
        """main prints exactly one integer followed by a newline"""
        with patch('sys.stdin', io.StringIO('100 2\n')):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                main()
                output = mock_out.getvalue()
                lines = output.split('\n')
                # Should be exactly one non-empty line
                non_empty = [line for line in lines if line.strip()]
                assert len(non_empty) == 1, (
                    f"Expected 1 line of output, got {len(non_empty)}: {output!r}"
                )
                assert non_empty[0].strip().isdigit(), (
                    f"Output should be integer, got: {non_empty[0]!r}"
                )

    def test_main_small_input(self):
        """main handles smallest valid input y=2, l=2"""
        with patch('sys.stdin', io.StringIO('2 2\n')):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                main()
                output = mock_out.getvalue().strip()
                assert int(output) == 10, f"Expected 10, got {output}"

    def test_main_large_input(self):
        """main handles large input y=10^18, l=2"""
        with patch('sys.stdin', io.StringIO('1000000000000000000 2\n')):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                main()
                output = mock_out.getvalue().strip()
                val = int(output)
                assert val >= 10, f"Expected >= 10, got {val}"


# ============================================================================
# Invariant tests
# ============================================================================
class TestInvariants:
    """Tests for documented invariants."""

    def test_invariant_base10_always_valid(self):
        """Base 10 is always a valid answer: y in base 10 is y >= l."""
        test_cases = [
            (2, 2), (10, 5), (100, 100), (9999, 42), (10**18, 2),
        ]
        for y, l_val in test_cases:
            result = solve(y, l_val)
            assert result >= 10, (
                f"Invariant violated: solve({y},{l_val}) = {result} < 10"
            )

    def test_invariant_valid_base_implies_digits_le_9(self):
        """For any valid base b, every digit must be in [0,9], so b >= 10."""
        import random
        random.seed(77)
        for _ in range(30):
            y = random.randint(2, 10**6)
            l_val = random.randint(2, y)
            b = solve(y, l_val)
            digits = to_base(y, b)
            assert digits is not None, (
                f"to_base({y}, {b}) returned None"
            )
            for d in digits:
                assert 0 <= d <= 9, (
                    f"Digit {d} out of range for y={y}, b={b}"
                )

    def test_invariant_base_bounded_by_y(self):
        """The answer base b satisfies b <= y."""
        import random
        random.seed(88)
        for _ in range(30):
            y = random.randint(2, 10**6)
            l_val = random.randint(2, y)
            b = solve(y, l_val)
            assert b <= y, f"solve({y},{l_val}) = {b} > y"

    def test_invariant_two_digit_constraints(self):
        """For k=2: y=a*b+c with a in [1,9], c in [0,9], b > max(a,c)."""
        import random
        random.seed(99)
        for _ in range(30):
            y = random.randint(11, 10000)
            b = solve_phase1_two_digit(y, 2)
            if b > 0:
                digits = to_base(y, b)
                assert digits is not None
                assert len(digits) == 2
                a, c = digits[0], digits[1]
                assert 1 <= a <= 9, f"Leading digit {a} not in [1,9]"
                assert 0 <= c <= 9, f"Second digit {c} not in [0,9]"
                assert b > max(a, c), f"b={b} not > max({a},{c})"
                assert y == a * b + c, f"y={y} != {a}*{b}+{c}"

    def test_invariant_three_digit_constraints(self):
        """For k=3: y=a*b^2+d*b+e with a in [1,9], d,e in [0,9], b > max(a,d,e)."""
        import random
        random.seed(101)
        for _ in range(50):
            y = random.randint(121, 100000)  # need at least 11^2 = 121 for 3 digits
            b = solve_phase2_three_digit(y, 2)
            if b > 0:
                digits = to_base(y, b)
                assert digits is not None
                assert len(digits) == 3, f"Expected 3 digits, got {len(digits)}"
                a, d, e = digits[0], digits[1], digits[2]
                assert 1 <= a <= 9
                assert 0 <= d <= 9
                assert 0 <= e <= 9
                assert b > max(a, d, e)
                assert y == a * b**2 + d * b + e

    def test_invariant_integer_kth_root_exact(self):
        """integer_kth_root returns r such that r^k <= n < (r+1)^k."""
        import random
        random.seed(55)
        for _ in range(50):
            n = random.randint(0, 10**15)
            k = random.randint(1, 10)
            r = integer_kth_root(n, k)
            assert r >= 0
            assert r**k <= n, f"r^k > n for r={r}, k={k}, n={n}"
            assert (r + 1) ** k > n, f"(r+1)^k <= n for r={r}, k={k}, n={n}"

    def test_invariant_reinterpret_non_negative(self):
        """reinterpret_base10 always returns >= 0."""
        test_lists = [[0], [0, 0, 0], [1], [9, 9, 9], [1, 0, 0, 0]]
        for digits in test_lists:
            result = reinterpret_base10(digits)
            assert result >= 0, f"Got negative for {digits}: {result}"

    def test_invariant_to_base_roundtrip_with_reinterpret(self):
        """For base 10, reinterpret_base10(to_base(y, 10)) == y."""
        for y in [0, 1, 9, 10, 99, 100, 12345, 999999999]:
            digits = to_base(y, 10)
            assert digits is not None
            result = reinterpret_base10(digits)
            assert result == y, (
                f"Roundtrip failed for y={y}: got {result}"
            )
