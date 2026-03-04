"""
Contract test suite for the solution module.
Tests are organized in four tiers:
  Tier 1: Unit tests for helpers (to_base, all_digits_valid, reinterpret_decimal, int_nth_root, check_base)
  Tier 2: Unit tests for search functions (search_d1, search_d2, search_d3, search_d_ge_4)
  Tier 3: Integration tests for solve
  Tier 4: End-to-end tests for main
  Plus invariant / property tests
"""

import pytest
import random
from unittest.mock import patch
from io import StringIO

from src.solution import (
    to_base,
    all_digits_valid,
    reinterpret_decimal,
    check_base,
    int_nth_root,
    search_d1,
    search_d2,
    search_d3,
    search_d_ge_4,
    solve,
    main,
)


# ============================================================
# Tier 1: Unit tests for helper functions
# ============================================================

class TestToBase:
    """Tests for to_base(y, b) -> DigitList"""

    def test_to_base_happy_10(self):
        """Convert 123 to base 10 returns [1,2,3]"""
        result = to_base(123, 10)
        assert result == [1, 2, 3], f"Expected [1,2,3], got {result}"

    def test_to_base_happy_2(self):
        """Convert 13 to base 2 returns [1,1,0,1]"""
        result = to_base(13, 2)
        assert result == [1, 1, 0, 1], f"Expected [1,1,0,1], got {result}"

    def test_to_base_zero(self):
        """Convert 0 to any base returns [0]"""
        result = to_base(0, 10)
        assert result == [0], f"Expected [0], got {result}"

    def test_to_base_one(self):
        """Convert 1 to base 2 returns [1]"""
        result = to_base(1, 2)
        assert result == [1], f"Expected [1], got {result}"

    def test_to_base_255_base16(self):
        """Convert 255 to base 16 returns [15, 15]"""
        result = to_base(255, 16)
        assert result == [15, 15], f"Expected [15, 15], got {result}"

    def test_to_base_base_equals_y(self):
        """Convert y to base y returns [1, 0]"""
        result = to_base(7, 7)
        assert result == [1, 0], f"Expected [1, 0], got {result}"

    def test_to_base_256_base2(self):
        """Convert 256 to base 2"""
        result = to_base(256, 2)
        assert result == [1, 0, 0, 0, 0, 0, 0, 0, 0], f"Expected [1,0,0,0,0,0,0,0,0], got {result}"

    def test_to_base_large_value_base10(self):
        """Convert 10^18 to base 10"""
        result = to_base(10**18, 10)
        assert result == [1] + [0]*18, f"Expected [1] + [0]*18, got {result}"

    def test_to_base_negative_y_error(self):
        """Negative y raises error"""
        with pytest.raises(Exception):
            to_base(-1, 10)

    def test_to_base_base_too_small_error(self):
        """Base < 2 raises error"""
        with pytest.raises(Exception):
            to_base(5, 1)

    def test_to_base_postcondition_roundtrip(self):
        """Digits reconstruct original value for base 7, y=1000"""
        result = to_base(1000, 7)
        b = 7
        reconstructed = sum(result[i] * b**(len(result)-1-i) for i in range(len(result)))
        assert reconstructed == 1000, f"Round-trip failed: {result} -> {reconstructed}"
        assert all(0 <= d < 7 for d in result), f"Digits out of range: {result}"
        assert result[0] > 0, f"Leading digit should be > 0 for y > 0"

    def test_to_base_roundtrip_base10(self):
        """to_base in base 10 round-trips correctly for large number"""
        result = to_base(9876543210, 10)
        assert result == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0], f"Expected [9,8,7,6,5,4,3,2,1,0], got {result}"

    def test_to_base_postcondition_leading_digit(self):
        """Leading digit is > 0 for y > 0, and len >= 1"""
        for y in [1, 2, 10, 100, 999]:
            for b in [2, 3, 10, 16]:
                result = to_base(y, b)
                assert len(result) >= 1, f"to_base({y}, {b}) returned empty list"
                assert result[0] > 0, f"to_base({y}, {b}): leading digit is 0, got {result}"

    def test_to_base_postcondition_all_digits_in_range(self):
        """All digits are in [0, b)"""
        for y, b in [(100, 3), (255, 2), (1000, 5), (12345, 12)]:
            result = to_base(y, b)
            assert all(0 <= d < b for d in result), f"to_base({y}, {b}): digit out of range in {result}"


class TestAllDigitsValid:
    """Tests for all_digits_valid(digits) -> bool"""

    def test_all_digits_valid_true(self):
        """All single decimal digits returns True"""
        assert all_digits_valid([1, 2, 3, 0, 9]) is True

    def test_all_digits_valid_false(self):
        """Digit 10 makes it invalid"""
        assert all_digits_valid([1, 10, 3]) is False

    def test_all_digits_valid_single_zero(self):
        """Single zero digit is valid"""
        assert all_digits_valid([0]) is True

    def test_all_digits_valid_single_nine(self):
        """Single 9 is valid"""
        assert all_digits_valid([9]) is True

    def test_all_digits_valid_boundary_10(self):
        """Digit exactly 10 is invalid"""
        assert all_digits_valid([10]) is False

    def test_all_digits_valid_all_nines(self):
        """List of all 9s is valid"""
        assert all_digits_valid([9, 9, 9, 9]) is True

    def test_all_digits_valid_mixed_boundary(self):
        """Mix of 0s and 9s is valid"""
        assert all_digits_valid([0, 9, 0, 9]) is True

    def test_all_digits_valid_large_digit(self):
        """Very large digit is invalid"""
        assert all_digits_valid([1, 2, 100]) is False


class TestReinterpretDecimal:
    """Tests for reinterpret_decimal(digits) -> int"""

    def test_reinterpret_decimal_happy(self):
        """Reinterpret [1,2,3] as 123"""
        assert reinterpret_decimal([1, 2, 3]) == 123

    def test_reinterpret_decimal_single(self):
        """Reinterpret [5] as 5"""
        assert reinterpret_decimal([5]) == 5

    def test_reinterpret_decimal_zero(self):
        """Reinterpret [0] as 0"""
        assert reinterpret_decimal([0]) == 0

    def test_reinterpret_decimal_leading_zero(self):
        """Reinterpret [0,1,2] as 12"""
        assert reinterpret_decimal([0, 1, 2]) == 12

    def test_reinterpret_decimal_empty_error(self):
        """Empty list raises error"""
        with pytest.raises(Exception):
            reinterpret_decimal([])

    def test_reinterpret_decimal_postcondition(self):
        """Verify postcondition formula"""
        digits = [3, 1, 4, 1, 5]
        result = reinterpret_decimal(digits)
        expected = sum(digits[i] * 10**(len(digits)-1-i) for i in range(len(digits)))
        assert result == expected == 31415


class TestIntNthRoot:
    """Tests for int_nth_root(x, n) -> int"""

    def test_int_nth_root_sqrt_perfect(self):
        """Square root of 49 is 7"""
        assert int_nth_root(49, 2) == 7

    def test_int_nth_root_sqrt_non_perfect(self):
        """Square root of 50 is 7"""
        assert int_nth_root(50, 2) == 7

    def test_int_nth_root_cube_root(self):
        """Cube root of 27 is 3"""
        assert int_nth_root(27, 3) == 3

    def test_int_nth_root_cube_root_non_perfect(self):
        """Cube root of 26 is 2"""
        assert int_nth_root(26, 3) == 2

    def test_int_nth_root_zero(self):
        """nth root of 0 is 0"""
        assert int_nth_root(0, 3) == 0

    def test_int_nth_root_one(self):
        """nth root of 1 is 1"""
        assert int_nth_root(1, 5) == 1

    def test_int_nth_root_n_equals_1(self):
        """1st root of x is x"""
        assert int_nth_root(42, 1) == 42

    def test_int_nth_root_large_cube(self):
        """Cube root of 10^18 is 10^6"""
        assert int_nth_root(10**18, 3) == 10**6

    def test_int_nth_root_large_cube_minus_one(self):
        """Cube root of 10^18-1 is 999999"""
        assert int_nth_root(10**18 - 1, 3) == 999999

    def test_int_nth_root_negative_x_error(self):
        """Negative x raises error"""
        with pytest.raises(Exception):
            int_nth_root(-1, 2)

    def test_int_nth_root_zero_degree_error(self):
        """n < 1 raises error"""
        with pytest.raises(Exception):
            int_nth_root(4, 0)

    def test_int_nth_root_postcondition_check(self):
        """Verify postcondition r^n <= x < (r+1)^n for large value"""
        x = 123456789012345678
        n = 4
        result = int_nth_root(x, n)
        assert result ** n <= x, f"{result}^{n} = {result**n} > {x}"
        assert (result + 1) ** n > x, f"{result+1}^{n} = {(result+1)**n} <= {x}"

    def test_int_nth_root_high_n(self):
        """60th root of 10^18 is small but correct"""
        x = 10**18
        n = 60
        result = int_nth_root(x, n)
        assert result >= 1, f"Expected >= 1, got {result}"
        assert result ** n <= x, f"{result}^{n} > {x}"
        assert (result + 1) ** n > x, f"({result}+1)^{n} <= {x}"

    def test_int_nth_root_powers_of_two(self):
        """Test perfect powers of 2"""
        assert int_nth_root(256, 8) == 2
        assert int_nth_root(1024, 10) == 2
        assert int_nth_root(1023, 10) == 1

    def test_int_nth_root_boundary_stress(self):
        """Stress test postconditions for various inputs"""
        test_cases = [
            (2, 2), (3, 2), (4, 2), (8, 3), (9, 2), (15, 4),
            (10**6, 3), (10**9, 3), (10**12, 4), (10**15, 5),
        ]
        for x, n in test_cases:
            r = int_nth_root(x, n)
            assert r >= 0, f"int_nth_root({x}, {n}) = {r} < 0"
            assert r ** n <= x, f"int_nth_root({x}, {n}) = {r}: {r}^{n} > {x}"
            assert (r + 1) ** n > x, f"int_nth_root({x}, {n}) = {r}: ({r}+1)^{n} <= {x}"


class TestCheckBase:
    """Tests for check_base(y, b, ell) -> bool"""

    def test_check_base_happy_true(self):
        """check_base(123, 10, 100) is True"""
        assert check_base(123, 10, 100) is True

    def test_check_base_happy_false_digits(self):
        """check_base(255, 16, 1) is False because digits [15,15] are > 9"""
        assert check_base(255, 16, 1) is False

    def test_check_base_false_ell(self):
        """check_base(5, 10, 6) is False because 5 < 6"""
        assert check_base(5, 10, 6) is False

    def test_check_base_true_boundary(self):
        """check_base(5, 10, 5) is True (5 >= 5)"""
        assert check_base(5, 10, 5) is True

    def test_check_base_invalid_y(self):
        """Negative y raises error"""
        with pytest.raises(Exception):
            check_base(-1, 10, 1)

    def test_check_base_invalid_base(self):
        """Base < 2 raises error"""
        with pytest.raises(Exception):
            check_base(5, 1, 1)

    def test_check_base_invalid_ell(self):
        """ell < 1 raises error"""
        with pytest.raises(Exception):
            check_base(5, 10, 0)

    def test_check_base_base10_always_valid(self):
        """Base 10 is always valid when ell <= y (invariant)"""
        for y in [1, 5, 9, 10, 100, 999999999, 10**18]:
            assert check_base(y, 10, 1) is True, f"check_base({y}, 10, 1) should be True"

    def test_check_base_base10_ell_equals_y(self):
        """Base 10: y reinterpreted is y itself, so y >= ell when ell == y"""
        for y in [1, 42, 1000]:
            assert check_base(y, 10, y) is True, f"check_base({y}, 10, {y}) should be True"


# ============================================================
# Tier 2: Unit tests for search functions
# ============================================================

class TestSearchD1:
    """Tests for search_d1(y, ell) -> SearchResult"""

    def test_search_d1_found(self):
        """y=5, ell=3: single digit 5 >= 3 => found with large sentinel"""
        result = search_d1(5, 3)
        assert result.found is True, "Expected found=True for y=5, ell=3"
        assert result.max_base >= 10**18, f"Expected large sentinel, got {result.max_base}"

    def test_search_d1_y_equals_9(self):
        """y=9, ell=1: found=True"""
        result = search_d1(9, 1)
        assert result.found is True
        assert result.max_base >= 10**18

    def test_search_d1_y_equals_ell(self):
        """y=7, ell=7: found=True"""
        result = search_d1(7, 7)
        assert result.found is True

    def test_search_d1_not_found_large_y(self):
        """y=10, ell=1: y > 9 => not found"""
        result = search_d1(10, 1)
        assert result.found is False
        assert result.max_base == -1

    def test_search_d1_not_found_ell_too_big(self):
        """y=3, ell=5: y < ell => not found"""
        result = search_d1(3, 5)
        assert result.found is False
        assert result.max_base == -1

    def test_search_d1_y_zero(self):
        """y=0, ell=1: 0 < 1 => not found (y < ell)"""
        # Note: contract says y >= 0, ell >= 1 and for solve ell <= y, but search_d1 precondition allows y=0
        result = search_d1(0, 1)
        assert result.found is False


class TestSearchD2:
    """Tests for search_d2(y, ell) -> SearchResult"""

    def test_search_d2_found(self):
        """y=21, ell=10: should find a valid 2-digit base"""
        result = search_d2(21, 10)
        assert result.found is True
        assert result.max_base >= 2
        # Verify the found base actually works
        digits = to_base(21, result.max_base)
        assert len(digits) == 2, f"Expected 2 digits, got {len(digits)}: {digits}"
        assert all_digits_valid(digits) is True
        assert reinterpret_decimal(digits) >= 10

    def test_search_d2_large_y(self):
        """y=10^18, ell=10: should find a valid 2-digit base"""
        result = search_d2(10**18, 10)
        assert result.found is True
        assert result.max_base >= 2

    def test_search_d2_not_found_small_y(self):
        """y=1, ell=1: too small for 2 digits"""
        result = search_d2(1, 1)
        assert result.found is False

    def test_search_d2_verify_check_base(self):
        """When found, check_base must confirm"""
        result = search_d2(100, 10)
        if result.found:
            assert check_base(100, result.max_base, 10) is True, \
                f"check_base(100, {result.max_base}, 10) should be True"

    def test_search_d2_y_11(self):
        """y=11, ell=10: base 11 gives [1,0] -> 10 >= 10"""
        result = search_d2(11, 10)
        assert result.found is True
        assert result.max_base >= 2
        assert check_base(11, result.max_base, 10) is True


class TestSearchD3:
    """Tests for search_d3(y, ell) -> SearchResult"""

    def test_search_d3_found(self):
        """y=100, ell=100: base 10 gives [1,0,0] -> 100 >= 100"""
        result = search_d3(100, 100)
        assert result.found is True
        assert result.max_base >= 2
        digits = to_base(100, result.max_base)
        assert len(digits) == 3, f"Expected 3 digits, got {len(digits)}: {digits}"
        assert check_base(100, result.max_base, 100) is True

    def test_search_d3_not_found_small_y(self):
        """y=3, ell=1: too small for 3 digits in any base"""
        result = search_d3(3, 1)
        assert result.found is False

    def test_search_d3_y_1000(self):
        """y=1000, ell=100: should find some valid 3-digit base"""
        result = search_d3(1000, 100)
        if result.found:
            assert result.max_base >= 2
            digits = to_base(1000, result.max_base)
            assert len(digits) == 3
            assert check_base(1000, result.max_base, 100) is True


class TestSearchDGe4:
    """Tests for search_d_ge_4(y, ell) -> SearchResult"""

    def test_search_d_ge_4_found(self):
        """y=10000, ell=1: base 10 gives 5 digits"""
        result = search_d_ge_4(10000, 1)
        assert result.found is True
        assert result.max_base >= 2
        digits = to_base(10000, result.max_base)
        assert len(digits) >= 4, f"Expected >= 4 digits, got {len(digits)}"
        assert check_base(10000, result.max_base, 1) is True

    def test_search_d_ge_4_small_y(self):
        """y=7, ell=1: very small, might not have 4-digit representation with valid digits"""
        result = search_d_ge_4(7, 1)
        # y=7 in base 2 is [1,1,1] which is 3 digits, not >= 4
        # so should be not found
        assert result.found is False

    def test_search_d_ge_4_y_16_base2(self):
        """y=16, ell=1: base 2 gives [1,0,0,0,0] = 5 digits, 10000 >= 1"""
        result = search_d_ge_4(16, 1)
        assert result.found is True
        assert check_base(16, result.max_base, 1) is True

    def test_search_d_ge_4_verify_digit_count(self):
        """When found, verify digit count is >= 4"""
        result = search_d_ge_4(100000, 1)
        if result.found:
            digits = to_base(100000, result.max_base)
            assert len(digits) >= 4, f"Expected >= 4 digits at base {result.max_base}, got {len(digits)}: {digits}"


# ============================================================
# Tier 3: Integration tests for solve
# ============================================================

class TestSolve:
    """Tests for solve(y, ell) -> int"""

    def test_solve_base10_fallback(self):
        """solve always returns >= 10"""
        result = solve(100, 100)
        assert result >= 10, f"Expected >= 10, got {result}"

    def test_solve_small_y_equals_ell_1(self):
        """solve(1, 1): y=ell=1, single digit => unbounded sentinel"""
        result = solve(1, 1)
        assert result >= 10**18, f"Expected >= 10^18, got {result}"

    def test_solve_y9_ell1(self):
        """solve(9, 1): single digit 9 >= 1 => unbounded"""
        result = solve(9, 1)
        assert result >= 10**18, f"Expected >= 10^18, got {result}"

    def test_solve_y10_ell1(self):
        """solve(10, 1): should find large base"""
        result = solve(10, 1)
        assert result >= 10, f"Expected >= 10, got {result}"
        assert check_base(10, result, 1) is True

    def test_solve_y10_ell10(self):
        """solve(10, 10): base 10 gives 10 >= 10"""
        result = solve(10, 10)
        assert result >= 10
        assert check_base(10, result, 10) is True

    def test_solve_y2_ell1(self):
        """solve(2, 1): y=2 is single digit => unbounded"""
        result = solve(2, 1)
        assert result >= 10**18

    def test_solve_y2_ell2(self):
        """solve(2, 2): y=2, ell=2, single digit 2>=2 => unbounded"""
        result = solve(2, 2)
        assert result >= 10**18

    def test_solve_validity_always(self):
        """solve result always passes check_base"""
        test_cases = [
            (500, 42), (12345, 100), (1000, 1), (999, 999),
            (100, 1), (10, 10), (50, 25),
        ]
        for y, ell in test_cases:
            result = solve(y, ell)
            assert result >= 10, f"solve({y}, {ell}) = {result} < 10"
            # For sentinel values, check_base might not apply if base is extremely large
            # but we can still verify for non-sentinel
            if result <= 10**18:
                assert check_base(y, result, ell) is True, \
                    f"check_base({y}, {result}, {ell}) should be True"

    def test_solve_large_y(self):
        """solve(10^18, 1): large y"""
        result = solve(10**18, 1)
        assert result >= 10
        if result <= 10**18:
            assert check_base(10**18, result, 1) is True

    def test_solve_y_out_of_range_low(self):
        """y=0 raises error"""
        with pytest.raises(Exception):
            solve(0, 0)

    def test_solve_ell_out_of_range(self):
        """ell > y raises error"""
        with pytest.raises(Exception):
            solve(5, 6)

    def test_solve_optimality_small(self):
        """For small y, verify no larger valid base exists (brute force check)"""
        for y in range(10, 51):
            for ell in [1, y // 2, y]:
                if ell < 1:
                    continue
                result = solve(y, ell)
                if result <= 10**18:
                    # Verify result+1 is not valid
                    next_base = result + 1
                    if next_base >= 2:
                        is_next_valid = check_base(y, next_base, ell)
                        assert is_next_valid is False, \
                            f"solve({y}, {ell})={result} but base {next_base} is also valid"

    def test_solve_brute_force_stress(self):
        """Brute-force stress test for y in [2..100], various ell values"""
        def brute_force_solve(y, ell):
            """O(y) brute force: check all bases from y down to 2"""
            best = -1
            for b in range(2, y + 2):
                digits = to_base(y, b)
                if all_digits_valid(digits) and reinterpret_decimal(digits) >= ell:
                    best = max(best, b)
            # For single digit: if y <= 9 and y >= ell, any base > y works => unbounded
            if y <= 9 and y >= ell:
                return 10**18 + 1  # sentinel
            return best

        for y in range(2, 101):
            for ell in [1, max(1, y // 2), y]:
                result = solve(y, ell)
                bf_result = brute_force_solve(y, ell)
                if bf_result >= 10**18:
                    assert result >= 10**18, \
                        f"solve({y}, {ell})={result}, brute_force={bf_result}: expected unbounded"
                else:
                    assert result == bf_result, \
                        f"solve({y}, {ell})={result}, brute_force={bf_result}: mismatch"

    def test_solve_monotonicity_in_ell(self):
        """solve(y, ell) should be non-increasing as ell increases (more restrictive)"""
        for y in [50, 100, 500, 1000]:
            prev_result = None
            for ell in range(1, y + 1, max(1, y // 20)):
                result = solve(y, ell)
                if prev_result is not None:
                    assert result <= prev_result, \
                        f"solve({y}, {ell})={result} > solve({y}, {ell - max(1, y//20)})={prev_result}: monotonicity violated"
                prev_result = result

    def test_solve_y_equals_ell(self):
        """When y == ell, base 10 gives reinterpretation = y = ell, so valid"""
        for y in [1, 5, 10, 100, 12345]:
            result = solve(y, y)
            assert result >= 10, f"solve({y}, {y}) = {result} < 10"


# ============================================================
# Tier 4: End-to-end tests for main
# ============================================================

class TestMain:
    """Tests for main() stdin/stdout"""

    def test_main_basic(self):
        """Basic main test with y=100, ell=10"""
        with patch('sys.stdin', StringIO("100 10\n")):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue().strip()
                result = int(output)
                assert result >= 10, f"Expected >= 10, got {result}"
                assert check_base(100, result, 10) is True

    def test_main_single_digit(self):
        """main with y=5, ell=1: unbounded"""
        with patch('sys.stdin', StringIO("5 1\n")):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue().strip()
                result = int(output)
                assert result >= 10**18, f"Expected >= 10^18 for single digit, got {result}"

    def test_main_output_format(self):
        """Output should be exactly one line with an integer followed by newline"""
        with patch('sys.stdin', StringIO("42 1\n")):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Should end with newline
                assert output.endswith('\n'), f"Output should end with newline: {repr(output)}"
                # Should be exactly one line
                lines = output.strip().split('\n')
                assert len(lines) == 1, f"Expected 1 line, got {len(lines)}: {lines}"
                # Should be a valid integer
                int(lines[0])  # Should not raise

    def test_main_malformed_input(self):
        """Malformed input should raise error"""
        with patch('sys.stdin', StringIO("abc\n")):
            with pytest.raises(Exception):
                main()

    def test_main_empty_input(self):
        """Empty input should raise error"""
        with patch('sys.stdin', StringIO("")):
            with pytest.raises(Exception):
                main()

    def test_main_y10_ell10(self):
        """main with y=10, ell=10"""
        with patch('sys.stdin', StringIO("10 10\n")):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue().strip()
                result = int(output)
                assert result >= 10
                assert check_base(10, result, 10) is True


# ============================================================
# Invariant tests
# ============================================================

class TestInvariants:
    """Tests for contract invariants"""

    def test_base10_always_valid(self):
        """Base 10 is always valid for any y with ell <= y"""
        for y in [1, 2, 5, 9, 10, 42, 100, 999, 10**6, 10**9, 999999999]:
            assert check_base(y, 10, 1) is True, \
                f"Invariant violated: check_base({y}, 10, 1) should be True"

    def test_base10_valid_ell_equals_y(self):
        """Base 10 with ell=y: reinterpretation is y itself, so y >= ell"""
        for y in [1, 10, 100, 12345, 999999]:
            assert check_base(y, 10, y) is True, \
                f"Invariant violated: check_base({y}, 10, {y}) should be True"

    def test_solve_always_ge_10(self):
        """solve result is always >= 10"""
        for y, ell in [(1, 1), (2, 1), (5, 5), (10, 1), (100, 50), (1000, 1)]:
            result = solve(y, ell)
            assert result >= 10, f"solve({y}, {ell}) = {result} < 10"

    def test_digit_count_relation(self):
        """For d-digit representation in base b: b^(d-1) <= y < b^d"""
        test_cases = [(100, 10), (255, 16), (1000, 7), (31, 2)]
        for y, b in test_cases:
            digits = to_base(y, b)
            d = len(digits)
            assert b ** (d - 1) <= y, f"b^(d-1) = {b}^{d-1} = {b**(d-1)} > {y}"
            assert y < b ** d, f"y = {y} >= b^d = {b}^{d} = {b**d}"

    def test_to_base_digit_sum_invariant(self):
        """Sum of digits * base^position always equals y"""
        random.seed(42)
        for _ in range(50):
            y = random.randint(0, 10**6)
            b = random.randint(2, 100)
            digits = to_base(y, b)
            reconstructed = sum(digits[i] * b**(len(digits)-1-i) for i in range(len(digits)))
            assert reconstructed == y, \
                f"to_base({y}, {b}) = {digits}, reconstructed = {reconstructed}"

    def test_d2_invariant_decomposition(self):
        """For d=2: y = a*b + c where a in [1,9], c in [0,9]"""
        # Pick a case we know has a 2-digit result
        y, b = 23, 11  # 23 = 2*11 + 1 => [2, 1]
        digits = to_base(y, b)
        if len(digits) == 2:
            a, c = digits
            assert y == a * b + c, f"{y} != {a}*{b} + {c}"
            assert 1 <= a <= 9
            assert 0 <= c <= 9

    def test_d3_invariant_decomposition(self):
        """For d=3: y = a*b^2 + c*b + e"""
        y, b = 100, 10  # [1, 0, 0]
        digits = to_base(y, b)
        if len(digits) == 3:
            a, c, e = digits
            assert y == a * b**2 + c * b + e
            assert 1 <= a <= 9
            assert 0 <= c <= 9
            assert 0 <= e <= 9


# ============================================================
# Property-based tests (using random, not hypothesis)
# ============================================================

class TestPropertyBased:
    """Property-based tests using random sampling"""

    def test_solve_result_is_valid(self):
        """For random (y, ell), solve result passes check_base"""
        random.seed(123)
        for _ in range(30):
            y = random.randint(1, 10**6)
            ell = random.randint(1, y)
            result = solve(y, ell)
            assert result >= 10
            if result <= 10**18:
                assert check_base(y, result, ell) is True, \
                    f"solve({y}, {ell})={result} but check_base fails"

    def test_solve_next_base_invalid(self):
        """For random (y, ell), solve(y,ell)+1 should be invalid (unless sentinel)"""
        random.seed(456)
        for _ in range(30):
            y = random.randint(10, 10**4)
            ell = random.randint(1, y)
            result = solve(y, ell)
            if result < 10**18:
                next_valid = check_base(y, result + 1, ell)
                assert next_valid is False, \
                    f"solve({y}, {ell})={result} but base {result+1} is also valid"

    def test_to_base_base10_reinterpret_identity(self):
        """to_base(y, 10) reinterpreted as decimal equals y"""
        random.seed(789)
        for _ in range(50):
            y = random.randint(0, 10**9)
            digits = to_base(y, 10)
            reinterpreted = reinterpret_decimal(digits)
            assert reinterpreted == y, \
                f"to_base({y}, 10)={digits}, reinterpret={reinterpreted} != {y}"

    def test_all_digits_valid_base10(self):
        """Digits of any number in base 10 are always valid decimal digits"""
        random.seed(101)
        for _ in range(50):
            y = random.randint(0, 10**12)
            digits = to_base(y, 10)
            assert all_digits_valid(digits) is True, \
                f"to_base({y}, 10)={digits} should all be valid decimal digits"

    def test_solve_monotone_ell(self):
        """solve(y, ell) is non-increasing in ell for fixed y"""
        random.seed(202)
        for _ in range(10):
            y = random.randint(10, 10**4)
            ells = sorted(random.sample(range(1, y + 1), min(10, y)))
            results = [solve(y, ell) for ell in ells]
            for i in range(len(results) - 1):
                assert results[i] >= results[i + 1], \
                    f"solve({y}, {ells[i]})={results[i]} < solve({y}, {ells[i+1]})={results[i+1]}: monotonicity violated"
