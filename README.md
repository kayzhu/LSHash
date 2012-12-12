LSHash
======

A fast Python implementation of locality sensitive hashing with persistance
support.

Highlights
---
* Fast hash calculation for large amount of high dimensional data through the
use of `numpy` arrays.
* Built-in support for persistency through Redis.
* Multiple hash indexes support.
* Built-in support for common distance/objective functions for ranking outputs.

Example Usage
---
To create 6-bit hashes for input data of 8 dimensions:

```python
>>> from LSHash import LSHash

>>> lsh = LSHash(6, 8)
>>>
>>> lsh.index([1,2,3,4,5,6,7,8])
>>> lsh.index([2,3,4,5,6,7,8,9])
>>> lsh.index([10,12,99,1,5,31,2,3])

>>> lsh.query([1,2,3,4,5,6,7,7])
[((1, 2, 3, 4, 5, 6, 7, 8), 1.0),
 ((2, 3, 4, 5, 6, 7, 8, 9), 3.3166247903553998)]

```
