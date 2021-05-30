#!/bin/bash

dirs=$1
# the directory
PY="python3.7 data/min_model.py"

fs=`ls ${dirs}/*.cnf`
for file in $fs
do
  $PY -p ${file} > ${file/\.cnf/\.m-m}&
done
