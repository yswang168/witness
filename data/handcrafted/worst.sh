#! /bin/bash

PY=python3.7


args=(-MUS -mc -mm)

for  i in 0 1 2 3 
do
   $PY ./data/worst.py 50 400 -m=1 ${args[$i]} > ./data/worst-wit-50-400-1-$i.txt&
done
for  i in 0 1 2 3
do
   $PY ./data/worst.py 50 400 -m=5 ${args[$i]} > ./data/worst-wit-50-400-5-$i.txt&
   $PY ./data/worst.py 50 400 -m=5 -cycle ${args[$i]} > ./data/worst-wit-50-400-5-$i-cycle.txt&
done
