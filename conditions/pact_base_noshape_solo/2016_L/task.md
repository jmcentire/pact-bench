# Swap Space

# Problem Description

# Problem Description

You administer a large cluster of computers with hard drives that use various file system types to store data. You recently decided to unify the file systems to the same type. That is quite a challenge since all the drives are currently in use, all of them are filled with important data to the limits of their capacities, and you cannot afford to lose any of the data. Moreover, reformatting a drive to use a new file system may significantly change the drive’s capacity. To make the reformat possible, you will have to buy an extra hard drive. Obviously, you want to save money by minimizing the size of such extra storage.

You can reformat the drives in any order. Prior to reformatting a drive, you must move all data from that drive to one or more other drives, splitting the data if necessary. After a drive is reformatted, you can immediately start using it to store data from other drives. It is not necessary to put all the data on the same drives they originally started on – in fact, this might even be impossible if some of the drives have smaller capacity with the new file system. It is also allowed for some data to end up on the extra drive.

As an example, suppose you have four drives A, B, C, and D with drive capacities 6, 1, 3, and 3 GB. Under the new file system, the capacities become 6, 7, 5, and 5 GB, respectively. If you buy only 1 GB of extra space, you can move the data from drive B there and then reformat drive B. Now you have 7 GB free on drive B, so you can move the 6 GB from drive A there and reformat drive A. Finally, you move the six total gigabytes from drives C and D to drive A, and reformat C and D.

## Input

The input begins with a line containing one integer \( n \) (\( 1 \leq n \leq 10^6 \)), which is the number of drives in your cluster. Following this are \( n \) lines, each describing a drive as two integers \( a \) and \( b \), where \( a \) is the capacity with the old file system and \( b \) is the capacity with the new file system.

All capacities are given in gigabytes and satisfy \( 1 \leq a, b \leq 10^9 \).

## Output

Display the total extra capacity in gigabytes you must buy to reformat the drives.

## Sample Input 1

```
4
6 6
1 7
3 5
3 5
```

## Sample Output 1

```
1
```

## Sample Input 2

```
4
2 2
3 3
5 1
5 10
```

## Sample Output 2

```
5
```

## Test Cases

A test harness with official test cases is provided in test_harness.py.
Run: `python test_harness.py solution.py`
