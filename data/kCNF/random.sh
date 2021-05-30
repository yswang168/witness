#!/bin/bash

# the directory
PY="python3.7 "
# for each of the dir in $1 to compute minimal witness 
for k in 3 #4 5 6
do
     # assert the current director is with cb_witness.py
     $PY ./data/run.py 50 200 -clen=$k > ./data/wit-$k-50-200-1.txt &
     $PY ./data/run.py 50 200 -clen=$k -mus > ./data/wit-$k-50-200-0.txt & # with mus solver
done
