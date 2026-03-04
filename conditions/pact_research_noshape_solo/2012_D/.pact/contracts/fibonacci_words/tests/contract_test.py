"""
Contract test suite for fibonacci_words component.
Tests organized in five tiers:
  Tier 1: Unit tests per function
  Tier 2: Brute-force oracle integration tests
  Tier 3: Property-based / invariant tests
  Tier 4: Error handling tests
  Tier 5: End-to-end & stress tests
"""

import re
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.fibonacci_words import (
    build_kmp_failure_table,
    count_overlapping,
    make_base_fib_state,
    combine_fib_states,
    solve,
    parse_input,
    format_output,
    main,
)


# ============================================================
# Helper: Brute-force Fibonacci word generation for oracle tests
# ============================================================

def _fib_word(n):
    """Generate the Fibonacci word F(n) by direct concatenation (small n only)."""
    if n == 0:
        return "0"
    if n == 1:
        return "1"
    a, b = "0", "1"
    for _ in range(2, n + 1):
        a, b = b, b + a
    return b


def _naive_count_overlapping(text, pattern):
    """Naive overlapping count for oracle comparison."""
    count = 0
    plen = len(pattern)
    for i in range(len(text) - plen + 1):
        if text[i:i + plen] == pattern:
            count += 1
    return count


# ============================================================
# Tier 1: Unit Tests — build_kmp_failure_table
# ============================================================

class TestBuildKmpFailureTable:
    def test_single_char(self):
        """KMP failure table for single character pattern '0'."""
        result = build_kmp_failure_table("0")
        assert result == [0], f"Expected [0], got {result}"
        assert len(result) == 1

    def test_repeated_chars(self):
        """KMP failure table for repeated pattern '0000'."""
        result = build_kmp_failure_table("0000")
        assert result == [0, 1, 2, 3], f"Expected [0, 1, 2, 3], got {result}"

    def test_alternating(self):
        """KMP failure table for alternating pattern '0101'."""
        result = build_kmp_failure_table("0101")
        assert result == [0, 0, 1, 2], f"Expected [0, 0, 1, 2], got {result}"

    def test_complex_pattern(self):
        """KMP failure table for '01001010'."""
        pattern = "01001010"
        result = build_kmp_failure_table(pattern)
        assert len(result) == 8, f"Expected length 8, got {len(result)}"
        assert result[0] == 0, "First entry must always be 0"

    def test_length_invariant(self):
        """KMP failure table length matches pattern length and bounds hold."""
        pattern = "010"
        result = build_kmp_failure_table(pattern)
        assert len(result) == len(pattern)
        assert result[0] == 0
        assert all(0 <= result[i] <= i for i in range(len(result))), \
            f"Bound violation in failure table: {result}"

    def test_prefix_suffix_property(self):
        """KMP table satisfies prefix==suffix property for all entries."""
        pattern = "010010"
        result = build_kmp_failure_table(pattern)
        for i in range(len(result)):
            if result[i] > 0:
                assert pattern[:result[i]] == pattern[i - result[i] + 1:i + 1], \
                    f"Prefix-suffix mismatch at index {i}: table={result[i]}"

    def test_empty_pattern_error(self):
        """KMP failure table raises error for empty pattern."""
        with pytest.raises(Exception):
            build_kmp_failure_table("")

    def test_two_chars_no_repeat(self):
        """KMP failure table for '01'."""
        result = build_kmp_failure_table("01")
        assert result == [0, 0], f"Expected [0, 0], got {result}"

    def test_two_chars_repeat(self):
        """KMP failure table for '00'."""
        result = build_kmp_failure_table("00")
        assert result == [0, 1], f"Expected [0, 1], got {result}"


# ============================================================
# Tier 1: Unit Tests — count_overlapping
# ============================================================

class TestCountOverlapping:
    def test_basic_non_overlapping(self):
        """Count non-overlapping occurrences of '01' in '0101'."""
        result = count_overlapping("0101", "01")
        assert result == 2, f"Expected 2, got {result}"

    def test_overlapping(self):
        """Count overlapping occurrences of '00' in '000'."""
        result = count_overlapping("000", "00")
        assert result == 2, f"Expected 2, got {result}"

    def test_no_match(self):
        """Count occurrences when pattern not in text."""
        result = count_overlapping("0000", "1")
        assert result == 0, f"Expected 0, got {result}"

    def test_full_match(self):
        """Count when text equals pattern exactly."""
        result = count_overlapping("010", "010")
        assert result == 1, f"Expected 1, got {result}"

    def test_text_shorter_than_pattern(self):
        """Count when text is shorter than pattern returns 0."""
        result = count_overlapping("0", "01")
        assert result == 0, f"Expected 0, got {result}"

    def test_empty_text(self):
        """Count with empty text returns 0."""
        result = count_overlapping("", "0")
        assert result == 0, f"Expected 0, got {result}"

    def test_empty_pattern_error(self):
        """Count raises error for empty pattern."""
        with pytest.raises(Exception):
            count_overlapping("010", "")

    def test_triple_overlap(self):
        """Count overlapping '010' in '01010' returns 2."""
        result = count_overlapping("01010", "010")
        assert result == 2, f"Expected 2, got {result}"

    def test_single_char_match(self):
        """Counting single char pattern in matching single char text."""
        result = count_overlapping("1", "1")
        assert result == 1, f"Expected 1, got {result}"

    def test_all_ones_overlap(self):
        """Counting '11' in '11111' returns 4 (overlapping)."""
        result = count_overlapping("11111", "11")
        assert result == 4, f"Expected 4, got {result}"

    def test_against_naive(self):
        """Verify count_overlapping against naive implementation for various inputs."""
        test_cases = [
            ("010101", "01"),
            ("000000", "00"),
            ("101010", "1010"),
            ("1", "1"),
            ("0", "1"),
            ("01010101", "0101"),
        ]
        for text, pattern in test_cases:
            result = count_overlapping(text, pattern)
            expected = _naive_count_overlapping(text, pattern)
            assert result == expected, \
                f"Mismatch for text='{text}', pattern='{pattern}': got {result}, expected {expected}"


# ============================================================
# Tier 1: Unit Tests — make_base_fib_state
# ============================================================

class TestMakeBaseFibState:
    def test_f0_long_pattern(self):
        """Base state for F(0)='0' with pattern longer than base string."""
        result = make_base_fib_state("0", "010")
        assert result.count == 0, f"Expected count=0, got {result.count}"
        assert result.length == 1, f"Expected length=1, got {result.length}"
        assert result.prefix == "0", f"Expected prefix='0', got '{result.prefix}'"
        assert result.suffix == "0", f"Expected suffix='0', got '{result.suffix}'"
        assert len(result.prefix) == 1
        assert len(result.suffix) == 1

    def test_f1_long_pattern(self):
        """Base state for F(1)='1' with pattern longer than base string."""
        result = make_base_fib_state("1", "010")
        assert result.count == 0, f"Expected count=0, got {result.count}"
        assert result.length == 1, f"Expected length=1, got {result.length}"
        assert result.prefix == "1", f"Expected prefix='1', got '{result.prefix}'"
        assert result.suffix == "1", f"Expected suffix='1', got '{result.suffix}'"

    def test_f0_exact_match(self):
        """Base state for F(0)='0' with pattern='0' (exact match)."""
        result = make_base_fib_state("0", "0")
        assert result.count == 1, f"Expected count=1, got {result.count}"
        assert result.length == 1, f"Expected length=1, got {result.length}"

    def test_f1_no_match(self):
        """Base state for F(1)='1' with pattern='0' (no match)."""
        result = make_base_fib_state("1", "0")
        assert result.count == 0, f"Expected count=0, got {result.count}"
        assert result.length == 1, f"Expected length=1, got {result.length}"

    def test_f1_exact_match(self):
        """Base state for F(1)='1' with pattern='1' (exact match)."""
        result = make_base_fib_state("1", "1")
        assert result.count == 1, f"Expected count=1, got {result.count}"
        assert result.length == 1

    def test_prefix_suffix_len_invariant(self):
        """Prefix and suffix length is min(1, len(pattern)-1)."""
        for pat in ["0", "01", "010", "0101"]:
            result = make_base_fib_state("0", pat)
            expected_len = min(1, len(pat) - 1)
            assert len(result.prefix) == expected_len, \
                f"For pattern='{pat}', prefix len={len(result.prefix)}, expected={expected_len}"
            assert len(result.suffix) == expected_len, \
                f"For pattern='{pat}', suffix len={len(result.suffix)}, expected={expected_len}"


# ============================================================
# Tier 1: Unit Tests — combine_fib_states
# ============================================================

class TestCombineFibStates:
    def test_combine_basic(self):
        """Combine F(1) and F(0) to get F(2) state with a known pattern."""
        # F(0)='0', F(1)='1', F(2)='10'
        pattern = "10"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        # F(2) = F(1) + F(0) = '10'
        result = combine_fib_states(f1, f0, pattern)
        # '10' contains '10' once
        assert result.count == 1, f"Expected count=1, got {result.count}"

    def test_combine_no_cross_boundary(self):
        """Combine where pattern doesn't span boundary."""
        pattern = "111"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        # F(2) = '10', no '111' present
        result = combine_fib_states(f1, f0, pattern)
        assert result.count == 0, f"Expected count=0, got {result.count}"

    def test_combine_with_cross_boundary(self):
        """Combine where pattern spans the join point."""
        pattern = "10"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        # F(2) = F(1) + F(0) = '1' + '0' = '10'
        # The pattern '10' spans the boundary
        result = combine_fib_states(f1, f0, pattern)
        assert result.count >= 0, "Count should be non-negative"
        # Verify against direct count
        f2_text = "10"
        expected = _naive_count_overlapping(f2_text, pattern)
        assert result.count == expected, f"Expected {expected}, got {result.count}"

    def test_combine_count_nonnegative(self):
        """Combined count is always non-negative."""
        pattern = "01"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        f2 = combine_fib_states(f1, f0, pattern)
        f3 = combine_fib_states(f2, f1, pattern)
        assert f2.count >= 0, f"F(2) count should be non-negative: {f2.count}"
        assert f3.count >= 0, f"F(3) count should be non-negative: {f3.count}"

    def test_combine_iterative_small(self):
        """Build F(5) via combine and compare to oracle."""
        pattern = "10"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        prev2, prev1 = f0, f1
        for k in range(2, 6):
            combined = combine_fib_states(prev1, prev2, pattern)
            prev2, prev1 = prev1, combined
        fib5 = _fib_word(5)
        expected = _naive_count_overlapping(fib5, pattern)
        assert prev1.count == expected, \
            f"F(5) count mismatch: got {prev1.count}, expected {expected}"

    def test_combine_prefix_suffix_length(self):
        """Verify prefix/suffix length invariants after combine."""
        pattern = "010"
        f0 = make_base_fib_state("0", pattern)
        f1 = make_base_fib_state("1", pattern)
        f2 = combine_fib_states(f1, f0, pattern)
        expected_ps_len = min(f2.length, len(pattern) - 1)
        assert len(f2.prefix) == expected_ps_len, \
            f"Prefix len={len(f2.prefix)}, expected={expected_ps_len}"
        assert len(f2.suffix) == expected_ps_len, \
            f"Suffix len={len(f2.suffix)}, expected={expected_ps_len}"


# ============================================================
# Tier 1: Unit Tests — format_output
# ============================================================

class TestFormatOutput:
    def test_basic(self):
        """Format case 1 with count 5."""
        result = format_output(1, 5)
        assert result == "Case 1: 5", f"Expected 'Case 1: 5', got '{result}'"

    def test_large_count(self):
        """Format case 3 with large count."""
        result = format_output(3, 1234567890)
        assert result == "Case 3: 1234567890", f"Expected 'Case 3: 1234567890', got '{result}'"

    def test_zero_count(self):
        """Format case 1 with count 0."""
        result = format_output(1, 0)
        assert result == "Case 1: 0", f"Expected 'Case 1: 0', got '{result}'"

    def test_regex_match(self):
        """Format output matches required regex pattern."""
        result = format_output(42, 99)
        assert re.match(r'^Case \d+: \d+$', result), \
            f"Output '{result}' does not match 'Case X: count' pattern"

    def test_case_number_preserved(self):
        """Case number in output equals input case_number."""
        for cn in [1, 5, 100]:
            result = format_output(cn, 0)
            assert f"Case {cn}:" in result, f"Case number {cn} not found in '{result}'"

    def test_count_preserved(self):
        """Count in output equals input count."""
        for cnt in [0, 1, 999999]:
            result = format_output(1, cnt)
            assert result.endswith(f": {cnt}"), f"Count {cnt} not at end of '{result}'"


# ============================================================
# Tier 1: Unit Tests — parse_input
# ============================================================

class TestParseInput:
    def test_single_case(self):
        """Parse single test case input."""
        result = parse_input("3\n010\n")
        assert len(result) == 1, f"Expected 1 test case, got {len(result)}"
        assert result[0].n == 3, f"Expected n=3, got {result[0].n}"
        assert result[0].pattern == "010", f"Expected pattern='010', got '{result[0].pattern}'"

    def test_multiple_cases(self):
        """Parse multiple test cases."""
        result = parse_input("5\n1\n10\n01\n")
        assert len(result) == 2, f"Expected 2 test cases, got {len(result)}"
        assert result[0].n == 5
        assert result[0].pattern == "1"
        assert result[1].n == 10
        assert result[1].pattern == "01"

    def test_whitespace_stripping(self):
        """Parse input with extra whitespace around lines."""
        result = parse_input("  3  \n  010  \n")
        assert len(result) == 1
        assert result[0].n == 3
        assert result[0].pattern == "010"

    def test_odd_lines_error(self):
        """Parse raises error for odd number of lines."""
        with pytest.raises(Exception):
            parse_input("3\n010\n5\n")

    def test_invalid_n_error(self):
        """Parse raises error for non-integer n."""
        with pytest.raises(Exception):
            parse_input("abc\n010\n")

    def test_n_out_of_range_error(self):
        """Parse raises error for n > 100."""
        with pytest.raises(Exception):
            parse_input("101\n010\n")

    def test_invalid_pattern_chars_error(self):
        """Parse raises error for pattern with invalid chars."""
        with pytest.raises(Exception):
            parse_input("3\n012\n")

    def test_empty_pattern_error(self):
        """Parse raises error for empty pattern line."""
        with pytest.raises(Exception):
            parse_input("3\n\n")

    def test_order_preserved(self):
        """TestCases are returned in input order."""
        result = parse_input("1\n0\n2\n1\n3\n01\n")
        assert len(result) == 3
        assert [tc.n for tc in result] == [1, 2, 3]
        assert [tc.pattern for tc in result] == ["0", "1", "01"]

    def test_boundary_n_values(self):
        """Parse accepts n=0 and n=100."""
        result = parse_input("0\n0\n100\n1\n")
        assert len(result) == 2
        assert result[0].n == 0
        assert result[1].n == 100

    def test_negative_n_error(self):
        """Parse raises error for negative n."""
        with pytest.raises(Exception):
            parse_input("-1\n010\n")


# ============================================================
# Tier 1: Unit Tests — solve
# ============================================================

class TestSolve:
    def test_f0_pattern_0(self):
        """Solve for F(0)='0' with pattern '0' returns 1."""
        result = solve(0, "0")
        assert result == 1, f"Expected 1, got {result}"

    def test_f0_pattern_1(self):
        """Solve for F(0)='0' with pattern '1' returns 0."""
        result = solve(0, "1")
        assert result == 0, f"Expected 0, got {result}"

    def test_f1_pattern_1(self):
        """Solve for F(1)='1' with pattern '1' returns 1."""
        result = solve(1, "1")
        assert result == 1, f"Expected 1, got {result}"

    def test_f1_pattern_0(self):
        """Solve for F(1)='1' with pattern '0' returns 0."""
        result = solve(1, "0")
        assert result == 0, f"Expected 0, got {result}"

    def test_f2_pattern_10(self):
        """Solve for F(2)='10' with pattern '10' returns 1."""
        result = solve(2, "10")
        assert result == 1, f"Expected 1, got {result}"

    def test_f3_pattern_1(self):
        """Solve for F(3)='101' with pattern '1' returns 2."""
        result = solve(3, "1")
        assert result == 2, f"Expected 2, got {result}"

    def test_nonnegative(self):
        """Solve always returns non-negative value."""
        result = solve(5, "010")
        assert result >= 0, f"Expected non-negative, got {result}"

    def test_n_negative_error(self):
        """Solve raises error for negative n."""
        with pytest.raises(Exception):
            solve(-1, "0")

    def test_n_too_large_error(self):
        """Solve raises error for n > 100."""
        with pytest.raises(Exception):
            solve(101, "0")

    def test_empty_pattern_error(self):
        """Solve raises error for empty pattern."""
        with pytest.raises(Exception):
            solve(5, "")

    def test_invalid_pattern_chars_error(self):
        """Solve raises error for pattern with invalid characters."""
        with pytest.raises(Exception):
            solve(5, "012")

    def test_f2_all_patterns(self):
        """Solve for F(2)='10' with all 1-2 char patterns."""
        # F(2) = '10'
        assert solve(2, "0") == 1
        assert solve(2, "1") == 1
        assert solve(2, "10") == 1
        assert solve(2, "01") == 0
        assert solve(2, "00") == 0
        assert solve(2, "11") == 0

    def test_f4(self):
        """Solve for F(4)='10110' with various patterns."""
        # F(4) = F(3) + F(2) = '101' + '10' = '10110'
        assert solve(4, "1") == 3
        assert solve(4, "0") == 2
        assert solve(4, "10") == 2
        assert solve(4, "01") == 1
        assert solve(4, "101") == 1
        assert solve(4, "10110") == 1


# ============================================================
# Tier 2: Brute-Force Oracle Integration Tests
# ============================================================

class TestOracleComparison:
    """Compare solve() against naive brute-force for small n."""

    def test_oracle_single_char_patterns(self):
        """Verify solve matches naive count for single char patterns across small n."""
        for n in range(16):
            fib = _fib_word(n)
            for pattern in ["0", "1"]:
                expected = _naive_count_overlapping(fib, pattern)
                result = solve(n, pattern)
                assert result == expected, \
                    f"Mismatch at n={n}, pattern='{pattern}': solve={result}, naive={expected}"

    def test_oracle_two_char_patterns(self):
        """Verify solve matches naive count for two char patterns across small n."""
        for n in range(16):
            fib = _fib_word(n)
            for pattern in ["00", "01", "10", "11"]:
                expected = _naive_count_overlapping(fib, pattern)
                result = solve(n, pattern)
                assert result == expected, \
                    f"Mismatch at n={n}, pattern='{pattern}': solve={result}, naive={expected}"

    def test_oracle_three_char_patterns(self):
        """Verify solve matches naive count for three char patterns."""
        for n in range(14):
            fib = _fib_word(n)
            for pattern in ["000", "001", "010", "011", "100", "101", "110", "111"]:
                expected = _naive_count_overlapping(fib, pattern)
                result = solve(n, pattern)
                assert result == expected, \
                    f"Mismatch at n={n}, pattern='{pattern}': solve={result}, naive={expected}"

    def test_oracle_longer_patterns(self):
        """Verify solve matches naive count for longer patterns at moderate n."""
        patterns = ["10110", "01011", "10101", "10110101", "1011010110"]
        for n in range(20):
            fib = _fib_word(n)
            for pattern in patterns:
                if len(pattern) <= len(fib):
                    expected = _naive_count_overlapping(fib, pattern)
                    result = solve(n, pattern)
                    assert result == expected, \
                        f"Mismatch at n={n}, pattern='{pattern}': solve={result}, naive={expected}"

    def test_oracle_pattern_longer_than_fib(self):
        """When pattern is longer than F(n), solve returns 0."""
        for n in range(8):
            fib = _fib_word(n)
            long_pattern = "0" * (len(fib) + 1)
            if len(long_pattern) <= 100000:
                result = solve(n, long_pattern)
                assert result == 0, \
                    f"Expected 0 for n={n}, pattern longer than F(n), got {result}"


# ============================================================
# Tier 3: Property-Based / Invariant Tests
# ============================================================

class TestRecurrenceProperty:
    """Verify the DP recurrence: solve(n,p) relates to solve(n-1,p) + solve(n-2,p) + cross."""

    def test_recurrence_holds(self):
        """solve(n) = solve(n-1) + solve(n-2) + cross for n>=2."""
        patterns = ["0", "1", "01", "10", "010", "101", "1011"]
        for pattern in patterns:
            for n in range(2, 16):
                sn = solve(n, pattern)
                sn1 = solve(n - 1, pattern)
                sn2 = solve(n - 2, pattern)
                cross = sn - sn1 - sn2
                assert cross >= 0, \
                    f"Negative cross-boundary for n={n}, pattern='{pattern}': " \
                    f"solve(n)={sn}, solve(n-1)={sn1}, solve(n-2)={sn2}, cross={cross}"
                assert sn == sn1 + sn2 + cross, \
                    f"Recurrence broken at n={n}, pattern='{pattern}'"

    def test_cross_boundary_matches_formula(self):
        """Verify cross-boundary formula against direct computation for small n."""
        pattern = "10"
        for n in range(2, 14):
            fn = _fib_word(n)
            fn1 = _fib_word(n - 1)
            fn2 = _fib_word(n - 2)
            total = _naive_count_overlapping(fn, pattern)
            c1 = _naive_count_overlapping(fn1, pattern)
            c2 = _naive_count_overlapping(fn2, pattern)
            cross = total - c1 - c2
            # cross should equal matches at the boundary
            assert cross >= 0, f"Negative cross at n={n}: total={total}, c1={c1}, c2={c2}"
            assert solve(n, pattern) == total, \
                f"solve({n}, '{pattern}') = {solve(n, pattern)} != {total}"


class TestSingleCharCountFibonacci:
    """Count of '0' and '1' in F(n) follows known Fibonacci-like patterns."""

    def test_count_of_0_sequence(self):
        """Count of '0' in F(n) should match a known sequence."""
        # F(0)='0': 1 zero, F(1)='1': 0 zeros, F(2)='10': 1 zero,
        # F(3)='101': 1 zero, F(4)='10110': 2 zeros, F(5)='10110101': 3 zeros
        expected_zeros = []
        for n in range(16):
            fib = _fib_word(n)
            expected_zeros.append(fib.count('0'))

        for n in range(16):
            result = solve(n, "0")
            assert result == expected_zeros[n], \
                f"Count of '0' in F({n}): solve={result}, expected={expected_zeros[n]}"

    def test_count_of_1_sequence(self):
        """Count of '1' in F(n) should match a known sequence."""
        expected_ones = []
        for n in range(16):
            fib = _fib_word(n)
            expected_ones.append(fib.count('1'))

        for n in range(16):
            result = solve(n, "1")
            assert result == expected_ones[n], \
                f"Count of '1' in F({n}): solve={result}, expected={expected_ones[n]}"


class TestCountNonNegativeInvariant:
    """solve() always returns non-negative values."""

    def test_nonnegative_across_range(self):
        """Solve returns non-negative for a range of n and patterns."""
        import random
        random.seed(42)
        for _ in range(50):
            n = random.randint(0, 100)
            plen = random.randint(1, 20)
            pattern = ''.join(random.choice('01') for _ in range(plen))
            result = solve(n, pattern)
            assert result >= 0, \
                f"Negative result for n={n}, pattern='{pattern}': {result}"


class TestPatternNotInAlphabet:
    """Pattern that cannot appear should return 0 for base cases."""

    def test_long_all_zeros_pattern(self):
        """Pattern '0000' never appears in small Fibonacci words (no consecutive zeros in Fib words for n>=2)."""
        # Actually Fibonacci words can have consecutive zeros for larger n.
        # But for base cases: F(0)='0', F(1)='1' - '0000' can't appear.
        assert solve(0, "0000") == 0
        assert solve(1, "0000") == 0


# ============================================================
# Tier 4: Additional Error Handling Tests
# ============================================================

class TestErrorHandling:
    def test_solve_n_boundary_low(self):
        """Solve accepts n=0."""
        result = solve(0, "0")
        assert result >= 0

    def test_solve_n_boundary_high(self):
        """Solve accepts n=100."""
        result = solve(100, "0")
        assert result >= 0

    def test_solve_n_just_below_range(self):
        """Solve rejects n=-1."""
        with pytest.raises(Exception):
            solve(-1, "0")

    def test_solve_n_just_above_range(self):
        """Solve rejects n=101."""
        with pytest.raises(Exception):
            solve(101, "0")

    def test_solve_pattern_with_spaces(self):
        """Solve rejects pattern with spaces."""
        with pytest.raises(Exception):
            solve(5, "0 1")

    def test_solve_pattern_with_letters(self):
        """Solve rejects pattern with letters."""
        with pytest.raises(Exception):
            solve(5, "0a1")

    def test_count_overlapping_empty_pattern(self):
        """count_overlapping rejects empty pattern."""
        with pytest.raises(Exception):
            count_overlapping("010", "")

    def test_build_kmp_empty_pattern(self):
        """build_kmp_failure_table rejects empty pattern."""
        with pytest.raises(Exception):
            build_kmp_failure_table("")


# ============================================================
# Tier 5: End-to-End & Stress Tests
# ============================================================

class TestMainEndToEnd:
    def test_main_single_case(self):
        """Main reads stdin with single case and writes correct output."""
        input_data = "3\n1\n"
        expected_count = solve(3, "1")
        expected_output = f"Case 1: {expected_count}\n"

        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert output == expected_output, \
                f"Expected '{expected_output}', got '{output}'"

    def test_main_multiple_cases(self):
        """Main handles multiple test cases with correct numbering."""
        input_data = "3\n1\n5\n010\n"
        count1 = solve(3, "1")
        count2 = solve(5, "010")
        expected_output = f"Case 1: {count1}\nCase 2: {count2}\n"

        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            assert output == expected_output, \
                f"Expected:\n{expected_output}\nGot:\n{output}"

    def test_main_output_format_exact(self):
        """Main output lines match 'Case X: count' regex with no trailing spaces."""
        input_data = "0\n0\n1\n1\n2\n10\n"

        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            lines = output.strip().split('\n')
            assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
            for i, line in enumerate(lines):
                assert re.match(r'^Case \d+: \d+$', line), \
                    f"Line {i + 1} doesn't match format: '{line}'"
                assert not line.endswith(' '), \
                    f"Line {i + 1} has trailing space: '{line}'"

    def test_main_case_numbering(self):
        """Main uses 1-based case numbering."""
        input_data = "0\n0\n0\n0\n0\n0\n"

        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()
            lines = output.strip().split('\n')
            for i, line in enumerate(lines):
                assert line.startswith(f"Case {i + 1}:"), \
                    f"Expected 'Case {i + 1}:', got '{line}'"


class TestStress:
    def test_solve_large_n_completes(self):
        """Solve with n=100 completes without error (stress test)."""
        result = solve(100, "010")
        assert result >= 0, f"Expected non-negative result, got {result}"

    def test_solve_large_n_long_pattern(self):
        """Solve with n=100 and a longer pattern completes."""
        pattern = "10110101" * 10  # 80 chars
        result = solve(100, pattern)
        assert result >= 0, f"Expected non-negative result, got {result}"

    def test_solve_large_n_single_char(self):
        """Solve with n=100 and single char pattern returns large count."""
        result_0 = solve(100, "0")
        result_1 = solve(100, "1")
        # F(100) has a known large length; counts should be positive
        assert result_0 > 0, f"Expected positive count of '0' in F(100), got {result_0}"
        assert result_1 > 0, f"Expected positive count of '1' in F(100), got {result_1}"
        # Total chars = count('0') + count('1') = len(F(100))
        # F(100) length = fib(101) in terms of the Fibonacci sequence starting 1,1,...
        # Just verify it's a very large number
        assert result_0 + result_1 > 10**10, \
            f"F(100) should be astronomically long, got total chars = {result_0 + result_1}"

    def test_solve_n100_count_0_plus_1_equals_length(self):
        """Count of '0' + count of '1' in F(n) equals len(F(n)) for small n, extrapolate property."""
        for n in range(20):
            fib = _fib_word(n)
            c0 = solve(n, "0")
            c1 = solve(n, "1")
            assert c0 + c1 == len(fib), \
                f"For n={n}: count('0')={c0} + count('1')={c1} != len(F(n))={len(fib)}"

    def test_solve_n100_performance(self):
        """Ensure solve(100, p) is fast for maximum-length pattern."""
        import time
        # Pattern of length ~1000
        pattern = ("10110101" * 125)[:1000]
        start = time.time()
        result = solve(100, pattern)
        elapsed = time.time() - start
        assert result >= 0
        # Should complete well within 10 seconds for a DP approach
        assert elapsed < 10.0, f"solve(100, pattern) took {elapsed:.2f}s, too slow"


# ============================================================
# Additional invariant tests
# ============================================================

class TestInvariants:
    def test_fibonacci_word_definition(self):
        """F(0)='0', F(1)='1', F(k)=F(k-1)+F(k-2) for k>=2."""
        assert _fib_word(0) == "0"
        assert _fib_word(1) == "1"
        for k in range(2, 15):
            assert _fib_word(k) == _fib_word(k - 1) + _fib_word(k - 2), \
                f"Fibonacci word definition violated at k={k}"

    def test_solve_consistent_with_count_overlapping_base(self):
        """For n=0 and n=1, solve equals count_overlapping on the base string."""
        for pattern in ["0", "1", "00", "01", "10", "11", "010", "101"]:
            assert solve(0, pattern) == count_overlapping("0", pattern), \
                f"solve(0, '{pattern}') != count_overlapping('0', '{pattern}')"
            assert solve(1, pattern) == count_overlapping("1", pattern), \
                f"solve(1, '{pattern}') != count_overlapping('1', '{pattern}')"

    def test_overlapping_semantics(self):
        """Verify overlapping semantics: '00' in '000' is 2, not 1."""
        assert count_overlapping("000", "00") == 2
        assert count_overlapping("0000", "00") == 3
        assert count_overlapping("00000", "00") == 4

    def test_no_pattern_means_zero(self):
        """If a pattern only contains chars not in the alphabet of Fib words, count is 0.
        Actually all patterns are '0'/'1' which IS the alphabet. Test a pattern
        that can't appear in any Fibonacci word for structural reasons."""
        # '00' never appears in Fibonacci words (proven property)
        # F(0)='0', F(1)='1', F(2)='10', F(3)='101', F(4)='10110'
        # Wait - '00' does NOT appear in Fibonacci words? Let's check F(5):
        # F(5) = F(4)+F(3) = '10110'+'101' = '10110101' -> no '00'
        # F(6) = F(5)+F(4) = '10110101'+'10110' = '1011010110110' -> has '00'? no wait...
        # Actually let me check: '1011010110110' - position 9,10 = '1','0' not '00'
        # Hmm, let me just verify by checking small n
        for n in range(15):
            fib = _fib_word(n)
            expected = _naive_count_overlapping(fib, "00")
            result = solve(n, "00")
            assert result == expected, \
                f"Mismatch for '00' in F({n}): solve={result}, expected={expected}"
