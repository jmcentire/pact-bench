"""
Contract test suite for trailing_digits_solver.

Tests are organized into three classes matching the three contract functions:
- TestParseInput: parsing logic
- TestSolve: core algorithm
- TestMain: end-to-end stdin/stdout
"""

import io
import sys
import pytest
from unittest.mock import patch
from math import gcd

# Import the component under test
from src.trailing_digits_solver import parse_input, solve, main


# ─── Helper: build the repdigit T_n = d repeated n times ───
def repdigit(d, n):
    """Return the integer formed by repeating digit d exactly n times. repdigit(4,3)==444."""
    if n == 0:
        return 0
    return d * ((10**n - 1) // 9)


# ═══════════════════════════════════════════════════════════════
# TestParseInput
# ═══════════════════════════════════════════════════════════════
class TestParseInput:
    """Tests for parse_input(line) -> ProblemInput."""

    # ── happy paths ──────────────────────────────────────────
    def test_parse_basic(self):
        result = parse_input("7 4 1000")
        assert result.b == 7, f"Expected b=7, got {result.b}"
        assert result.d == 4, f"Expected d=4, got {result.d}"
        assert result.a == 1000, f"Expected a=1000, got {result.a}"

    def test_parse_large_a(self):
        large_a = 10**100
        line = f"999999999 9 {large_a}"
        result = parse_input(line)
        assert result.b == 999999999
        assert result.d == 9
        assert result.a == large_a, "a should be a large Python int"

    def test_parse_d_zero(self):
        result = parse_input("5 0 100")
        assert result.b == 5
        assert result.d == 0
        assert result.a == 100

    def test_parse_min_values(self):
        result = parse_input("1 0 1")
        assert result.b == 1
        assert result.d == 0
        assert result.a == 1

    def test_parse_max_b_max_d(self):
        result = parse_input("1000000000 9 1000000000")
        assert result.b == 1000000000
        assert result.d == 9
        assert result.a == 1000000000

    # ── edge: whitespace handling ────────────────────────────
    def test_parse_extra_whitespace(self):
        result = parse_input("  7   4   1000  ")
        assert result.b == 7
        assert result.d == 4
        assert result.a == 1000

    def test_parse_tabs_and_spaces(self):
        result = parse_input("\t7\t4\t1000\t")
        assert result.b == 7
        assert result.d == 4
        assert result.a == 1000

    # ── error: wrong_token_count ─────────────────────────────
    @pytest.mark.parametrize("line,desc", [
        ("", "empty string"),
        ("42", "single token"),
        ("7 4", "two tokens"),
        ("7 4 1000 extra", "four tokens"),
        ("1 2 3 4 5", "five tokens"),
    ])
    def test_parse_wrong_token_count(self, line, desc):
        with pytest.raises(Exception, match=r".*"):
            parse_input(line)

    # ── error: non_integer_token ─────────────────────────────
    @pytest.mark.parametrize("line,desc", [
        ("7 abc 1000", "letters in d"),
        ("hello 4 1000", "letters in b"),
        ("7 4 world", "letters in a"),
        ("7 4.5 1000", "float in d"),
        ("7.0 4 1000", "float in b"),
        ("7 4 10.0", "float in a"),
    ])
    def test_parse_non_integer_token(self, line, desc):
        with pytest.raises(Exception, match=r".*"):
            parse_input(line)


# ═══════════════════════════════════════════════════════════════
# TestSolve
# ═══════════════════════════════════════════════════════════════
class TestSolve:
    """Tests for solve(b, d, a) -> int."""

    # ── happy paths / known answers ──────────────────────────
    def test_b1_d5_a55555(self):
        """b=1: every integer is a multiple. 55555 has 5 trailing 5s."""
        assert solve(1, 5, 55555) == 5

    def test_b1_d1_a11111(self):
        assert solve(1, 1, 11111) == 5

    def test_b3_d3_a333(self):
        """3*111=333 has 3 trailing 3s."""
        assert solve(3, 3, 333) == 3

    def test_b3_d3_a332(self):
        """333 > 332 so n=3 not achievable; 33=3*11 is ok => n=2."""
        assert solve(3, 3, 332) == 2

    def test_b9_d9_a99(self):
        """9*11=99 has 2 trailing 9s."""
        assert solve(9, 9, 99) == 2

    def test_b9_d9_a98(self):
        """99 > 98, so n=2 not achievable; 9 is ok => n=1."""
        assert solve(9, 9, 98) == 1

    # ── d == 0 cases ─────────────────────────────────────────
    def test_d0_b10_a1000(self):
        """1000 = 10*100 has 3 trailing zeros."""
        assert solve(10, 0, 1000) == 3

    def test_d0_b3_a100(self):
        """Multiples of 3 <= 100: 30,60,90 have 1 trailing zero each. No 2-zero multiple <=100 exists (300>100). Answer=1."""
        assert solve(3, 0, 100) == 1

    def test_d0_b5_a100(self):
        """5*20=100 has 2 trailing zeros."""
        assert solve(5, 0, 100) == 2

    def test_d0_b1_a1000(self):
        """b=1, d=0: 1000 has 3 trailing zeros."""
        assert solve(1, 0, 1000) == 3

    def test_d0_b1_a10000(self):
        assert solve(1, 0, 10000) == 4

    # ── no match cases ───────────────────────────────────────
    def test_even_b_odd_d(self):
        """Even multiples never end in an odd digit."""
        assert solve(2, 1, 100) == 0
        assert solve(2, 3, 100) == 0
        assert solve(2, 5, 1000) == 0
        assert solve(2, 7, 10000) == 0
        assert solve(2, 9, 100000) == 0

    def test_b5_d3(self):
        """Multiples of 5 end in 0 or 5; never 3."""
        assert solve(5, 3, 10000) == 0

    # ── b > a ────────────────────────────────────────────────
    def test_b_greater_than_a(self):
        assert solve(100, 5, 50) == 0

    def test_b_much_greater_than_a(self):
        assert solve(1000000000, 1, 1) == 0

    # ── b == a ───────────────────────────────────────────────
    def test_b_equals_a_match(self):
        """Only multiple is b itself. 7 ends in 7."""
        assert solve(7, 7, 7) == 1

    def test_b_equals_a_no_match(self):
        """Only multiple is 7, which doesn't end in 3."""
        assert solve(7, 3, 7) == 0

    # ── a == 1 ───────────────────────────────────────────────
    def test_a1_b1_d1(self):
        """Only multiple is 1, which ends in 1."""
        assert solve(1, 1, 1) == 1

    def test_a1_b1_d2(self):
        """Only multiple is 1, which doesn't end in 2."""
        assert solve(1, 2, 1) == 0

    def test_a1_b1_d0(self):
        """Only multiple is 1, which doesn't end in 0."""
        assert solve(1, 0, 1) == 0

    # ── b == 1 (all numbers are multiples) ───────────────────
    def test_b1_d4_a4444(self):
        """4444 has 4 trailing 4s, and 44444 > 4444."""
        assert solve(1, 4, 4444) == 4

    def test_b1_d4_a44444(self):
        assert solve(1, 4, 44444) == 5

    def test_b1_d4_a44443(self):
        """44444 > 44443, so n=5 not achievable; 4444 <= 44443 => n=4."""
        assert solve(1, 4, 44443) == 4

    # ── large a (big integer arithmetic) ─────────────────────
    def test_large_a_b1_d7(self):
        """b=1, d=7, a=10^50: repdigit 777...7 (50 digits) < 10^50 so answer=50."""
        assert solve(1, 7, 10**50) == 50

    def test_large_a_b1_d7_exact_repdigit(self):
        """a is exactly the 50-digit repdigit of 7s."""
        a = repdigit(7, 50)
        assert solve(1, 7, a) == 50

    def test_large_a_b1_d7_one_less(self):
        """a = repdigit(7,50) - 1: the 50-digit repdigit doesn't fit."""
        a = repdigit(7, 50) - 1
        result = solve(1, 7, a)
        assert result == 49, f"Expected 49 trailing 7s, got {result}"

    # ── postcondition: result range invariant ────────────────
    @pytest.mark.parametrize("b,d,a", [
        (1, 0, 1),
        (1, 5, 55555),
        (2, 1, 100),
        (7, 4, 1000),
        (3, 3, 333),
        (10, 0, 1000),
        (100, 5, 50),
        (999999999, 9, 10**20),
        (1, 9, 10**100),
    ])
    def test_result_in_valid_range(self, b, d, a):
        result = solve(b, d, a)
        max_digits = len(str(a))
        assert 0 <= result <= max_digits, (
            f"solve({b}, {d}, {a}) = {result} not in [0, {max_digits}]"
        )

    # ── postcondition: verify trailing digits when n > 0 ────
    @pytest.mark.parametrize("b,d,a", [
        (1, 5, 55555),
        (3, 3, 333),
        (9, 9, 99),
        (1, 7, 10**50),
        (10, 0, 1000),
        (5, 0, 100),
        (7, 7, 7),
        (1, 4, 4444),
        (3, 0, 100),
        (1, 1, 1),
    ])
    def test_verify_existence_of_valid_multiple(self, b, d, a):
        """If solve returns n > 0, verify a valid k*b exists with correct trailing digits."""
        n = solve(b, d, a)
        if n == 0:
            # Verify no multiple of b in [b, a] has last digit == d
            # (Checking all is infeasible for large a, so just spot-check first few)
            count = min(a // b, 1000)
            for k in range(1, count + 1):
                last_digit = (k * b) % 10
                assert last_digit != d, (
                    f"solve({b},{d},{a})=0 but {k}*{b}={k*b} ends in {d}"
                )
            return

        target = repdigit(d, n)
        M = 10**n
        # Find smallest k such that k*b ≡ target (mod M)
        g = gcd(b, M)
        assert target % g == 0, "Target should be divisible by gcd(b, M)"
        b_red = b // g
        M_red = M // g
        t_red = target // g
        k0 = (t_red * pow(b_red, -1, M_red)) % M_red
        if k0 == 0:
            k0 = M_red
        val = k0 * b
        assert val <= a, (
            f"solve({b},{d},{a})={n} but smallest k*b={val} > a={a}"
        )
        assert val % M == target, (
            f"solve({b},{d},{a})={n} but {val} mod {M} = {val % M} != {target}"
        )

    # ── postcondition: n+1 is not achievable ─────────────────
    @pytest.mark.parametrize("b,d,a", [
        (3, 3, 332),
        (9, 9, 98),
        (1, 4, 44443),
        (5, 5, 55),
    ])
    def test_next_level_not_achievable(self, b, d, a):
        """Verify that n+1 trailing digits is NOT achievable."""
        n = solve(b, d, a)
        next_n = n + 1
        if next_n > len(str(a)):
            return  # trivially not achievable
        target = repdigit(d, next_n)
        M = 10**next_n
        g = gcd(b, M)
        if target % g != 0:
            return  # not solvable at all — correct
        b_red = b // g
        M_red = M // g
        t_red = target // g
        k0 = (t_red * pow(b_red, -1, M_red)) % M_red
        if k0 == 0:
            k0 = M_red
        val = k0 * b
        assert val > a, (
            f"solve({b},{d},{a})={n} but n+1={next_n} IS achievable: {k0}*{b}={val} <= {a}"
        )

    # ── invariant: answer monotonically reachable ────────────
    def test_all_smaller_n_achievable_when_n_achieved(self):
        """If n trailing d's are achievable, then n-1 trailing d's should also be achievable
        (because the same k*b has the right last n-1 digits too). This means solve should
        return the maximum n, and we verify n >= 1 implies n-1 would also work."""
        b, d, a = 3, 3, 333
        n = solve(b, d, a)
        assert n == 3
        # Verify that smaller values are also achievable
        for sub_n in range(1, n):
            target = repdigit(d, sub_n)
            M = 10**sub_n
            g = gcd(b, M)
            assert target % g == 0
            b_red = b // g
            M_red = M // g
            t_red = target // g
            k0 = (t_red * pow(b_red, -1, M_red)) % M_red
            if k0 == 0:
                k0 = M_red
            assert k0 * b <= a, (
                f"sub_n={sub_n} should be achievable but smallest k*b={k0*b} > {a}"
            )

    # ── invariant: all intermediate values are ints ──────────
    def test_return_type_is_int(self):
        result = solve(7, 4, 1000)
        assert isinstance(result, int), f"Expected int, got {type(result)}"

    # ── special: d=0, T_n always 0 ───────────────────────────
    def test_d0_repdigit_is_zero(self):
        """When d=0, repdigit is always 0 for any n, meaning we seek divisibility by 10^n."""
        for n in range(0, 10):
            assert repdigit(0, n) == 0


# ═══════════════════════════════════════════════════════════════
# TestMain
# ═══════════════════════════════════════════════════════════════
class TestMain:
    """End-to-end tests for main(), patching stdin and capturing stdout."""

    def _run_main(self, stdin_text):
        """Helper: run main() with given stdin text, return captured stdout."""
        captured = io.StringIO()
        with patch("sys.stdin", io.StringIO(stdin_text)), \
             patch("sys.stdout", captured):
            main()
        return captured.getvalue()

    # ── happy paths ──────────────────────────────────────────
    def test_main_b3_d3_a333(self):
        output = self._run_main("3 3 333\n")
        assert output == "3\n", f"Expected '3\\n', got {output!r}"

    def test_main_b1_d5_a55555(self):
        output = self._run_main("1 5 55555\n")
        assert output == "5\n", f"Expected '5\\n', got {output!r}"

    def test_main_no_match(self):
        output = self._run_main("2 1 100\n")
        assert output == "0\n", f"Expected '0\\n', got {output!r}"

    def test_main_b9_d9_a99(self):
        output = self._run_main("9 9 99\n")
        assert output == "2\n", f"Expected '2\\n', got {output!r}"

    def test_main_d0(self):
        output = self._run_main("10 0 1000\n")
        assert output == "3\n", f"Expected '3\\n', got {output!r}"

    # ── output format ────────────────────────────────────────
    def test_output_ends_with_single_newline(self):
        output = self._run_main("9 9 99\n")
        assert output.endswith("\n"), "Output should end with newline"
        assert not output.endswith("\n\n"), "Output should not end with double newline"
        stripped = output.strip()
        assert stripped.isdigit(), f"Output should be a non-negative integer, got {stripped!r}"

    def test_output_is_single_line(self):
        output = self._run_main("3 3 333\n")
        lines = output.splitlines()
        assert len(lines) == 1, f"Expected exactly 1 line of output, got {len(lines)}"

    # ── error: empty stdin ───────────────────────────────────
    def test_empty_stdin_raises(self):
        with pytest.raises(Exception):
            self._run_main("")

    # ── error: malformed input ───────────────────────────────
    def test_malformed_input_two_tokens(self):
        with pytest.raises(Exception):
            self._run_main("7 4\n")

    def test_malformed_input_non_integer(self):
        with pytest.raises(Exception):
            self._run_main("7 abc 1000\n")

    def test_malformed_input_four_tokens(self):
        with pytest.raises(Exception):
            self._run_main("7 4 1000 extra\n")
