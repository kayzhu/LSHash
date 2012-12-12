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

Quickstart
---
To create 6-bit hashes for input data of 8 dimensions:

```python
>>> from LSHash import LSHash

>>> lsh = LSHash(6, 8)
>>> lsh.index([1,2,3,4,5,6,7,8])
>>> lsh.index([2,3,4,5,6,7,8,9])
>>> lsh.index([10,12,99,1,5,31,2,3])
>>> lsh.query([1,2,3,4,5,6,7,7])
[((1, 2, 3, 4, 5, 6, 7, 8), 1.0),
 ((2, 3, 4, 5, 6, 7, 8, 9), 3.3166247903553998)]

```

Main Interface
---

* To initialize:

```python
LSHash(hash_size, input_dim, num_of_hashtables=1, storage=None,
       matrices_filename=None, overwrite=False)
```

parameters:

```
hash_size:
    The length of the resulting binary hash.
input_dim:
    The dimension of the input vector.
num_hashtables = 1:
    (optional) The number of hash tables used for multiple lookups.
storage = None:
    (optional) Specify the name of the storage to be used for the index
    storage. Options include "redis".
matrices_filename = None:
    (optional) Specify the path to the .npz file random matrices are stored
    or to be stored if the file does not exist yet
overwrite = False:
    (optional) Whether to overwrite the matrices file if it already exist
```

* To index a data point of a given `LSHash` instance, e.g., `lsh`:

```python
lsh.index(input_point, extra_data=None):
```

parameters:

```
input_point:
    The input data point is an array or tuple of numbers of input_dim.
extra_data = None:
    (optional) Extra data to be added along with the input_point.
```

* To query a data point against a given `LSHash` instance, e.g., `lsh`:

```python
lsh.query(query_point, num_results=None, distance_func="euclidian"):

```

parameters:

```
query_point:
    The query data point is an array or tuple of numbers of input_dim.
num_results = None:
    (optional) The number of query results to return in ranked order. By
    default all results will be returned.
distance_func = "euclidian":
    (optional) Distance function to use to rank the candidates. By default
    euclidian distance function will be used.
```





