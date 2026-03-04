# Trailing Digits

# Problem Description

## Problem Description

A large shipment of doodads has just arrived, and each doodad has a suggested retail price of \( b \) cents. Consumers are more likely to purchase goods when most of the trailing digits are the same. For example, items are more likely to be priced at 99 cents rather than 57 cents. To make your goods more appealing, you’ve decided to sell your goods in bundles. To make a bundle, you choose a positive integer \( k \), and sell \( k \) doodads for \( k \times b \) cents. With an appropriate choice of \( k \), you can have a more pleasing price. For example, selling 57-cent doodads in bundles of size 7 means that each bundle sells for 399 cents, which has two trailing 9s, rather than no trailing 9s of 57. This idea of trailing 9s can be generalized to any other trailing digit: bundles of 692 57-cent doodads sell for 39,444 cents (three trailing 4s) and bundles of one million doodads sell for 57,000,000 cents (six trailing 0s).

After some thought, you realize that you do not want to make your bundles too large—not only can the price be excessive, but who really needs several million doodads? For any type of doodad, your marketing department has a maximum bundle price of \( a \).

Given the price of a doodad, the desired trailing digit, and the maximum price of a bundle, write a program that optimizes the trailing digits.

## Input

Input consists of a single line containing three integers \( b \), \( d \), and \( a \), where \( b \) (\( 1 \leq b < 10^6 \)) is the price of a doodad in cents, \( d \) (\( 0 \leq d \leq 9 \)) is the desired trailing digit, and \( a \) (\( b \leq a < 10^{10,000} \)) is the maximum price of a bundle.

## Output

Output the maximum number of consecutive occurrences of \( d \) that can appear at the end of a bundle price, given that the price of the bundle cannot exceed \( a \).

## Sample Input and Output

```plaintext
Sample Input 1
57 9 1000
Sample Output 1
2
```

```plaintext
Sample Input 2
57 4 40000
Sample Output 2
3
```

```plaintext
Sample Input 3
57 4 39000
Sample Output 3
2
```

## Test Cases

A test harness with official test cases is provided in test_harness.py.
Run: `python test_harness.py solution.py`
