# Forever Young

# Problem Description

## Problem Description

My birthday is coming up. Alas, I am getting old and would like to feel young again. Fortunately, I have come up with an excellent way of feeling younger: if I write my age as a number in an appropriately chosen base \( b \), then it appears to be smaller. For instance, suppose my age in base 10 is 32. Written in base 16 it is only 20!

However, I cannot choose an arbitrary base when doing this. If my age written in base \( b \) contains digits other than 0 to 9, then it will be obvious that I am cheating, which defeats the purpose. In addition, if my age written in base \( b \) is too small then it would again be obvious that I am cheating.

Given my age \( y \) and a lower bound \( \ell \) on how small I want my age to appear, find the largest base \( b \) such that \( y \) written in base \( b \) contains only decimal digits, and is at least \( \ell \) when interpreted as a number in base 10.

### Input

The input consists of a single line containing two base 10 integers \( y \) (10 ≤ \( y \) ≤ \( 10^{18} \) – yes, I am very old) and \( \ell \) (10 ≤ \( \ell \) ≤ \( y \)).

### Output

Display the largest base \( b \) as described above.

### Sample Input 1

```
32 20
```

### Sample Output 1

```
16
```

### Sample Input 2

```
2016 100
```

### Sample Output 2

```
42
```

## Test Cases

A test harness with official test cases is provided in test_harness.py.
Run: `python test_harness.py solution.py`
