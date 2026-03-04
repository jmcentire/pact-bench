# Fibonacci Words

# Problem Description

## Problem Description

The Fibonacci word sequence of bit strings is defined as:

\[ F(n) = 
\begin{cases} 
0 & \text{if } n = 0 \\
1 & \text{if } n = 1 \\
F(n-1) + F(n-2) & \text{if } n \geq 2 
\end{cases} \]

Here `+` denotes concatenation of strings. The first few elements are:

\[
\begin{align*}
n & \quad F(n) \\
0 & \quad 0 \\
1 & \quad 1 \\
2 & \quad 10 \\
3 & \quad 101 \\
4 & \quad 10110 \\
5 & \quad 10110101 \\
6 & \quad 1011010110110 \\
7 & \quad 101101011011010110101 \\
8 & \quad 1011010110110101101011011010110110 \\
9 & \quad 1011010110110101101011011010110110101101011011010110101 \\
\end{align*}
\]

Given a bit pattern `p` and a number `n`, determine how often `p` occurs in `F(n)`.

## Input

- The first line of each test case contains the integer \( n \) \((0 \leq n \leq 100)\).
- The second line contains the bit pattern `p`. The pattern `p` is nonempty and has a length of at most 100,000 characters.

## Output

- For each test case, display its case number followed by the number of occurrences of the bit pattern `p` in `F(n)`. Occurrences may overlap.
- The number of occurrences will be less than \( 2^{63} \).

## Sample Input

```
6
10
7
10
6
01
6
101
96
10110101101101
```

## Sample Output

```
Case 1: 5
Case 2: 8
Case 3: 4
Case 4: 4
Case 5: 7540113804746346428
```

## Test Cases

A test harness with official test cases is provided in test_harness.py.
Run: `python test_harness.py solution.py`
