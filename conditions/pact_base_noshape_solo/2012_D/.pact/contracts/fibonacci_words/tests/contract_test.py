"""
Contract test suite for fibonacci_words component.
Tests are organized in four tiers:
  Tier 1: build_failure unit tests
  Tier 2: count_overlapping unit tests
  Tier 3: solve oracle-based tests
  Tier 4: main I/O integration tests
  Plus invariant and property-based tests using random.
"""
import pytest
import sys
import io
import random
from unittest.mock import patch

from src.fibonacci_words import build_failure, count_overlapping, solve, main


# ============================================================
# Helper: generate Fibonacci words for oracle testing
# ============================================================
def fib_word(n):
    """Generate the n-th Fibonacci word by definition."""
    if n == 0:
        return "0"
    if n == 1:
        return "1"
    a, b = "0", "1"
    for _ in range(2, n + 1):
        a, b = b, b + a
    return b


def naive_count(text, pattern):
    """Brute-force count of overlapping occurrences of pattern in text."""
    count = 0
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        count += 1
        start = pos + 1
    return count


def fib_number(n):
    """Compute the n-th Fibonacci number (fib(0)=0, fib(1)=1, fib(2)=1, ...)."""
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# ============================================================
# TIER 1: build_failure tests
# ============================================================
class TestBuildFailure:
    def test_single_char_0(self):
        """build_failure with '0' returns [0]."""
        result = build_failure("0")
        assert result == [0], f"Expected [0], got {result}"

    def test_single_char_1(self):
        """build_failure with '1' returns [0]."""
        result = build_failure("1")
        assert result == [0], f"Expected [0], got {result}"

    def test_pattern_00(self):
        """build_failure with '00' returns [0, 1]."""
        result = build_failure("00")
        assert result == [0, 1], f"Expected [0, 1], got {result}"

    def test_pattern_01(self):
        """build_failure with '01' returns [0, 0]."""
        result = build_failure("01")
        assert result == [0, 0], f"Expected [0, 0], got {result}"

    def test_pattern_010(self):
        """build_failure with '010' returns [0, 0, 1]."""
        result = build_failure("010")
        assert result == [0, 0, 1], f"Expected [0, 0, 1], got {result}"

    def test_pattern_0101(self):
        """build_failure with '0101' returns [0, 0, 1, 2]."""
        result = build_failure("0101")
        assert result == [0, 0, 1, 2], f"Expected [0, 0, 1, 2], got {result}"

    def test_pattern_00100(self):
        """build_failure with '00100' returns [0, 1, 0, 1, 2]."""
        result = build_failure("00100")
        assert result == [0, 1, 0, 1, 2], f"Expected [0, 1, 0, 1, 2], got {result}"

    def test_all_ones(self):
        """build_failure with '11111' returns [0, 1, 2, 3, 4]."""
        result = build_failure("11111")
        assert result == [0, 1, 2, 3, 4], f"Expected [0,1,2,3,4], got {result}"

    def test_result_length_equals_pattern_length(self):
        """build_failure result has same length as input pattern."""
        pattern = "01010"
        result = build_failure(pattern)
        assert len(result) == len(pattern), (
            f"Expected length {len(pattern)}, got {len(result)}"
        )

    def test_empty_pattern_raises_error(self):
        """build_failure raises an error on empty pattern."""
        with pytest.raises(Exception):
            build_failure("")

    def test_invariant_bounds(self):
        """Failure table values satisfy 0 <= failure[i] <= i."""
        pattern = "010100101"
        result = build_failure(pattern)
        for i in range(len(result)):
            assert 0 <= result[i] <= i, (
                f"failure[{i}] = {result[i]} violates bounds [0, {i}]"
            )

    def test_invariant_first_zero(self):
        """Failure table first element is always 0."""
        for pattern in ["0", "1", "01", "10", "010", "0101", "11111"]:
            result = build_failure(pattern)
            assert result[0] == 0, (
                f"failure[0] = {result[0]} for pattern '{pattern}', expected 0"
            )


# ============================================================
# TIER 2: count_overlapping tests
# ============================================================
class TestCountOverlapping:
    def test_basic_non_overlapping(self):
        """count_overlapping finds occurrences of '01' in '0101'."""
        pattern = "01"
        failure = build_failure(pattern)
        result = count_overlapping("0101", pattern, failure)
        assert result == 2, f"Expected 2, got {result}"

    def test_overlapping_matches(self):
        """count_overlapping finds overlapping occurrences of '010' in '01010'."""
        pattern = "010"
        failure = build_failure(pattern)
        result = count_overlapping("01010", pattern, failure)
        assert result == 2, f"Expected 2, got {result}"

    def test_single_char_count(self):
        """count_overlapping counts '0' in '00100'."""
        pattern = "0"
        failure = build_failure(pattern)
        result = count_overlapping("00100", pattern, failure)
        assert result == 3, f"Expected 3, got {result}"

    def test_full_match(self):
        """count_overlapping returns 1 when pattern equals text."""
        pattern = "010"
        failure = build_failure(pattern)
        result = count_overlapping("010", pattern, failure)
        assert result == 1, f"Expected 1, got {result}"

    def test_pattern_longer_than_text(self):
        """count_overlapping returns 0 when pattern is longer than text."""
        pattern = "010"
        failure = build_failure(pattern)
        result = count_overlapping("01", pattern, failure)
        assert result == 0, f"Expected 0, got {result}"

    def test_empty_text(self):
        """count_overlapping returns 0 for empty text."""
        pattern = "0"
        failure = build_failure(pattern)
        result = count_overlapping("", pattern, failure)
        assert result == 0, f"Expected 0, got {result}"

    def test_no_match(self):
        """count_overlapping returns 0 when pattern not in text."""
        pattern = "1"
        failure = build_failure(pattern)
        result = count_overlapping("0000", pattern, failure)
        assert result == 0, f"Expected 0, got {result}"

    def test_all_overlapping_00_in_0000(self):
        """count_overlapping counts all overlapping '00' in '0000'."""
        pattern = "00"
        failure = build_failure(pattern)
        result = count_overlapping("0000", pattern, failure)
        assert result == 3, f"Expected 3, got {result}"

    def test_error_empty_pattern(self):
        """count_overlapping raises error on empty pattern."""
        with pytest.raises(Exception):
            count_overlapping("010", "", [])

    def test_error_failure_length_mismatch(self):
        """count_overlapping raises error when failure table length mismatches pattern."""
        pattern = "01"
        # Provide a failure table of wrong length
        wrong_failure = [0, 0, 0]  # length 3 != length 2
        with pytest.raises(Exception):
            count_overlapping("010", pattern, wrong_failure)


# ============================================================
# TIER 3: solve tests — oracle-based and analytical
# ============================================================
class TestSolve:
    def test_f0_pattern_0(self):
        """solve(0, '0') returns 1 since F(0)='0'."""
        result = solve(0, "0")
        assert result == 1, f"Expected 1, got {result}"

    def test_f0_pattern_1(self):
        """solve(0, '1') returns 0 since F(0)='0'."""
        result = solve(0, "1")
        assert result == 0, f"Expected 0, got {result}"

    def test_f1_pattern_1(self):
        """solve(1, '1') returns 1 since F(1)='1'."""
        result = solve(1, "1")
        assert result == 1, f"Expected 1, got {result}"

    def test_f1_pattern_0(self):
        """solve(1, '0') returns 0 since F(1)='1'."""
        result = solve(1, "0")
        assert result == 0, f"Expected 0, got {result}"

    def test_f2_pattern_10(self):
        """solve(2, '10') returns 1 since F(2)='10'."""
        result = solve(2, "10")
        assert result == 1, f"Expected 1, got {result}"

    def test_f0_long_pattern(self):
        """solve(0, '00') returns 0 since F(0)='0' is shorter than pattern."""
        result = solve(0, "00")
        assert result == 0, f"Expected 0, got {result}"

    def test_oracle_small_n_various_patterns(self):
        """For n in [0..18], verify solve matches brute-force naive counting."""
        # Pre-generate Fibonacci words up to n=18
        fib_words = {}
        for n in range(19):
            fib_words[n] = fib_word(n)

        # Test patterns: single chars, short patterns, substrings
        test_patterns = ["0", "1", "01", "10", "010", "101", "0101", "1010",
                         "00", "11", "001", "100", "01001"]

        for n in range(19):
            fw = fib_words[n]
            for pattern in test_patterns:
                expected = naive_count(fw, pattern)
                result = solve(n, pattern)
                assert result == expected, (
                    f"solve({n}, '{pattern}') = {result}, "
                    f"expected {expected} (F({n}) = '{fw[:50]}...')"
                )

    def test_oracle_boundary_spanning_patterns(self):
        """Test patterns that span the boundary between F(k-1) and F(k-2) in concatenation."""
        for n in range(3, 16):
            fw = fib_word(n)
            # Take a substring that spans the boundary
            fk1_len = len(fib_word(n - 1))
            if fk1_len > 2 and fk1_len < len(fw) - 2:
                # Pattern crossing boundary
                start = fk1_len - 2
                end = fk1_len + 2
                pattern = fw[start:end]
                if len(pattern) >= 1:
                    expected = naive_count(fw, pattern)
                    result = solve(n, pattern)
                    assert result == expected, (
                        f"Boundary pattern test failed: solve({n}, '{pattern}') = {result}, "
                        f"expected {expected}"
                    )

    def test_f10_count_zeros(self):
        """solve(10, '0') counts zeros in F(10).
        F(10) has fib(9)=34 zeros (the count of '0' in F(n) is fib(n-1) for n>=2,
        and F(0)='0', F(1)='1')."""
        # F(n) has length fib(n+1) (using fib(1)=1, fib(2)=1, ...).
        # Number of '0's in F(n): for n>=2, it's fib(n-1).
        # Let's verify with oracle for n=10.
        fw = fib_word(10)
        expected = fw.count("0")
        result = solve(10, "0")
        assert result == expected, f"Expected {expected}, got {result}"

    def test_f10_count_ones(self):
        """solve(10, '1') counts ones in F(10)."""
        fw = fib_word(10)
        expected = fw.count("1")
        result = solve(10, "1")
        assert result == expected, f"Expected {expected}, got {result}"

    def test_large_n_single_char_0(self):
        """solve(50, '0') returns the count of 0s in F(50).
        The number of '0's in F(n) follows Fibonacci-like recurrence.
        For F(0)='0': count_0=1. F(1)='1': count_0=0.
        For k>=2: count_0(k) = count_0(k-1) + count_0(k-2).
        So count_0(n) for n>=0 can be computed."""
        # count_0(0) = 1, count_0(1) = 0
        # count_0(k) = count_0(k-1) + count_0(k-2)
        c0 = [0] * 51
        c0[0] = 1
        c0[1] = 0
        for k in range(2, 51):
            c0[k] = c0[k - 1] + c0[k - 2]
        expected = c0[50]
        result = solve(50, "0")
        assert result == expected, f"Expected {expected}, got {result}"

    def test_large_n_single_char_1(self):
        """solve(50, '1') returns the count of 1s in F(50)."""
        # count_1(0) = 0, count_1(1) = 1
        # count_1(k) = count_1(k-1) + count_1(k-2)
        c1 = [0] * 51
        c1[0] = 0
        c1[1] = 1
        for k in range(2, 51):
            c1[k] = c1[k - 1] + c1[k - 2]
        expected = c1[50]
        result = solve(50, "1")
        assert result == expected, f"Expected {expected}, got {result}"

    def test_n100_single_char_0(self):
        """solve(100, '0') returns a very large number (count of 0s in F(100))."""
        c0 = [0] * 101
        c0[0] = 1
        c0[1] = 0
        for k in range(2, 101):
            c0[k] = c0[k - 1] + c0[k - 2]
        expected = c0[100]
        result = solve(100, "0")
        assert result == expected, f"Expected {expected}, got {result}"
        assert result > 0, "Count should be positive"

    def test_solve_nonnegative(self):
        """solve always returns a non-negative count."""
        result = solve(10, "010")
        assert result >= 0, f"Expected non-negative, got {result}"

    def test_error_n_negative(self):
        """solve raises error when n < 0."""
        with pytest.raises(Exception):
            solve(-1, "0")

    def test_error_n_too_large(self):
        """solve raises error when n > 100."""
        with pytest.raises(Exception):
            solve(101, "0")

    def test_error_empty_pattern(self):
        """solve raises error on empty pattern."""
        with pytest.raises(Exception):
            solve(5, "")

    def test_error_invalid_pattern_chars(self):
        """solve raises error when pattern contains non-binary characters."""
        with pytest.raises(Exception):
            solve(5, "012")

    def test_error_invalid_pattern_letters(self):
        """solve raises error when pattern contains letters."""
        with pytest.raises(Exception):
            solve(5, "abc")

    def test_pattern_longer_than_fib_word(self):
        """solve returns 0 when pattern is longer than F(n)."""
        # F(3) = '101' (length 3), pattern of length 5
        result = solve(3, "10110")
        # F(3) = '101', so pattern '10110' can't appear
        assert result == 0, f"Expected 0, got {result}"


# ============================================================
# TIER 3b: Monotonicity and recurrence invariant tests
# ============================================================
class TestSolveInvariants:
    def test_monotonicity_for_various_patterns(self):
        """For k>=2, count(k, p) >= count(k-1, p) and count(k, p) >= count(k-2, p)."""
        patterns = ["0", "1", "10", "01", "010", "101"]
        for pattern in patterns:
            counts = []
            for n in range(20):
                counts.append(solve(n, pattern))
            for k in range(2, 20):
                assert counts[k] >= counts[k - 1], (
                    f"Monotonicity violated: count({k}, '{pattern}') = {counts[k]} "
                    f"< count({k-1}, '{pattern}') = {counts[k-1]}"
                )
                assert counts[k] >= counts[k - 2], (
                    f"Monotonicity violated: count({k}, '{pattern}') = {counts[k]} "
                    f"< count({k-2}, '{pattern}') = {counts[k-2]}"
                )

    def test_recurrence_lower_bound(self):
        """For k>=2, count(k) >= count(k-1) + count(k-2) (cross matches >= 0)."""
        patterns = ["01", "10", "0", "1", "010"]
        for pattern in patterns:
            counts = []
            for n in range(20):
                counts.append(solve(n, pattern))
            for k in range(2, 20):
                assert counts[k] >= counts[k - 1] + counts[k - 2], (
                    f"Recurrence lower bound violated: count({k}, '{pattern}') = {counts[k]} "
                    f"< count({k-1}) + count({k-2}) = {counts[k-1]} + {counts[k-2]}"
                )

    def test_random_oracle_small_n(self):
        """For random (n, pattern) pairs with small n, verify solve matches naive oracle."""
        random.seed(42)
        fib_words = {n: fib_word(n) for n in range(19)}
        for _ in range(50):
            n = random.randint(0, 18)
            fw = fib_words[n]
            if len(fw) == 0:
                continue
            # Generate a random binary pattern of length 1..min(10, len(fw))
            max_pat_len = min(10, len(fw))
            pat_len = random.randint(1, max_pat_len)
            pattern = "".join(random.choice("01") for _ in range(pat_len))
            expected = naive_count(fw, pattern)
            result = solve(n, pattern)
            assert result == expected, (
                f"Random oracle failed: solve({n}, '{pattern}') = {result}, "
                f"expected {expected}"
            )

    def test_random_oracle_with_fib_substrings(self):
        """Test solve with substrings taken directly from Fibonacci words."""
        random.seed(123)
        fib_words = {n: fib_word(n) for n in range(19)}
        for _ in range(30):
            n = random.randint(4, 18)
            fw = fib_words[n]
            # Pick a random substring of fw as pattern
            pat_len = random.randint(1, min(20, len(fw)))
            start = random.randint(0, len(fw) - pat_len)
            pattern = fw[start:start + pat_len]
            expected = naive_count(fw, pattern)
            result = solve(n, pattern)
            assert result == expected, (
                f"Substring oracle failed: solve({n}, '{pattern}') = {result}, "
                f"expected {expected}"
            )


# ============================================================
# TIER 4: main() I/O integration tests
# ============================================================
class TestMain:
    def test_single_case(self):
        """main correctly processes a single test case."""
        # F(6) and pattern '10'
        fw6 = fib_word(6)
        expected_count = naive_count(fw6, "10")
        input_data = "6\n10\n"
        expected_output = f"Case 1: {expected_count}\n"

        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == expected_output, (
                    f"Expected '{expected_output}', got '{mock_stdout.getvalue()}'"
                )

    def test_multiple_cases(self):
        """main correctly processes multiple test cases."""
        fw3 = fib_word(3)
        fw5 = fib_word(5)
        count1 = naive_count(fw3, "10")
        count2 = naive_count(fw5, "01")
        input_data = "3\n10\n5\n01\n"
        expected_output = f"Case 1: {count1}\nCase 2: {count2}\n"

        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == expected_output, (
                    f"Expected '{expected_output}', got '{mock_stdout.getvalue()}'"
                )

    def test_empty_input(self):
        """main produces no output on empty input."""
        input_data = ""
        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == "", (
                    f"Expected empty output, got '{mock_stdout.getvalue()}'"
                )

    def test_whitespace_only_input(self):
        """main produces no output when input is only whitespace/blank lines."""
        input_data = "\n\n  \n\n"
        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == "", (
                    f"Expected empty output, got '{mock_stdout.getvalue()}'"
                )

    def test_output_format_case_numbering(self):
        """Output lines follow exact format 'Case {i}: {count}' with 1-indexing."""
        input_data = "0\n0\n1\n1\n"
        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                lines = mock_stdout.getvalue().strip().split("\n")
                assert len(lines) == 2, f"Expected 2 output lines, got {len(lines)}"
                assert lines[0].startswith("Case 1: "), (
                    f"First line should start with 'Case 1: ', got '{lines[0]}'"
                )
                assert lines[1].startswith("Case 2: "), (
                    f"Second line should start with 'Case 2: ', got '{lines[1]}'"
                )

    def test_output_lines_newline_terminated(self):
        """Each output line ends with a newline."""
        input_data = "0\n0\n"
        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert output.endswith("\n"), (
                    f"Output should end with newline, got '{output}'"
                )

    def test_error_odd_lines(self):
        """main raises error on odd number of non-empty lines (incomplete test case)."""
        input_data = "5\n"
        with patch("sys.stdin", io.StringIO(input_data)):
            with pytest.raises(Exception):
                # Capture stdout to avoid side effects
                with patch("sys.stdout", new_callable=io.StringIO):
                    main()

    def test_error_non_integer_n(self):
        """main raises error when n is not a valid integer."""
        input_data = "abc\n010\n"
        with patch("sys.stdin", io.StringIO(input_data)):
            with pytest.raises(Exception):
                with patch("sys.stdout", new_callable=io.StringIO):
                    main()

    def test_three_cases(self):
        """main correctly processes three test cases with correct ordering."""
        fw0 = fib_word(0)
        fw1 = fib_word(1)
        fw4 = fib_word(4)
        c1 = naive_count(fw0, "0")
        c2 = naive_count(fw1, "1")
        c3 = naive_count(fw4, "10")
        input_data = "0\n0\n1\n1\n4\n10\n"
        expected_output = f"Case 1: {c1}\nCase 2: {c2}\nCase 3: {c3}\n"

        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == expected_output, (
                    f"Expected '{expected_output}', got '{mock_stdout.getvalue()}'"
                )

    def test_trailing_blank_lines(self):
        """main handles trailing blank lines gracefully."""
        fw2 = fib_word(2)
        expected_count = naive_count(fw2, "1")
        input_data = "2\n1\n\n\n"
        expected_output = f"Case 1: {expected_count}\n"

        with patch("sys.stdin", io.StringIO(input_data)):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                assert mock_stdout.getvalue() == expected_output, (
                    f"Expected '{expected_output}', got '{mock_stdout.getvalue()}'"
                )


# ============================================================
# Additional invariant: KMP failure table prefix/suffix property
# ============================================================
class TestKMPFailureInvariant:
    def test_failure_prefix_suffix_property(self):
        """For all i, pattern[0:failure[i]] == pattern[i-failure[i]+1:i+1]."""
        patterns = ["010100101", "0101010101", "001001001", "1100110011"]
        for pattern in patterns:
            failure = build_failure(pattern)
            for i in range(len(pattern)):
                f_val = failure[i]
                if f_val > 0:
                    prefix = pattern[0:f_val]
                    suffix = pattern[i - f_val + 1:i + 1]
                    assert prefix == suffix, (
                        f"KMP invariant violated at i={i} for pattern '{pattern}': "
                        f"prefix '{prefix}' != suffix '{suffix}', failure[{i}]={f_val}"
                    )

    def test_failure_maximality(self):
        """The failure value is the LONGEST proper prefix that is also a suffix.
        Verify by checking no larger value would work."""
        patterns = ["010100101", "001001001", "0101"]
        for pattern in patterns:
            failure = build_failure(pattern)
            for i in range(len(pattern)):
                f_val = failure[i]
                # Check that f_val + 1 would NOT be valid (unless f_val == i, which can't happen
                # since it's a PROPER prefix)
                for candidate in range(f_val + 1, i + 1):
                    prefix = pattern[0:candidate]
                    suffix = pattern[i - candidate + 1:i + 1]
                    assert prefix != suffix, (
                        f"Failure table not maximal at i={i} for pattern '{pattern}': "
                        f"failure[{i}]={f_val} but candidate {candidate} also works"
                    )
