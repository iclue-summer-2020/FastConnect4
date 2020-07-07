# FastConnect4
Faster implementation of Connect 4 with bitboards
Also includes an implementation of Connect 4 with arrays as a comparison

Times (on my machine) to run 500 games to completion
```
$ time python3 array.py 

real	0m4.830s
user	0m4.454s
sys	0m0.043s
$ time python3 bitboard.py 

real	0m0.727s
user	0m0.691s
sys	0m0.024s
```
