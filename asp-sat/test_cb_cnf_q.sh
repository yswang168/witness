#!/bin/bash

# the directory
PY="python3.7 cb_witness.py"

first_witness()
{
dirs=$1
for file in `ls ${dirs}/*.m`
do
 if [ ! -f $file-m ]; then
  if [ -s $file ]; then
    st="`grep ^UNSAT $file`"
  fi
  if [ ! -z "$st" ]; then
    continue
  fi
  line=`cat $file`
  line=${line/\[/}
  line=${line/\]/}
  line=${line/\n/}
  line=${line//,/}
  echo $line > $file-m
 fi
  Fcnf=${file/\.m/\.cnf}
  echo "$PY -t 7200 -v4 -TT_PYSAT -q $Fcnf $file-m"
  $PY -t 7200  -v4 -TT_PYSAT -check_compact -q $Fcnf $file-m
done
}

second_witness()
{

dirs=$1
for file in `ls ${dirs}/*.m-m`
do
  if [ -s $file ]; then
    st="`grep ^UNSAT $file`"
  fi
  if [ ! -z "$st" ]; then
    continue
  fi
  sed -i '/SAT/d' $file # remove the line which looks like "SATISFIABLE" 
  Fcnf=${file/\.m-m/\.cnf}
  Fwit=${file/\.m-m/\.wit}
  #$PY-t 7200  -v4 -TT_PYSAT -mh  -MUS_Solver=picomus -q $Fcnf $file 
  if [[ $# -ge 2 && $2 -eq 1 ]];
   then
      echo "$PY -t 7200 -v4 -TT_PYSAT -MUS_Solver=picomus  -q -mh -check_compact  $Fcnf $file"
      $PY -t 7200  -v4 -TT_PYSAT -check_compact -q -mh -MUS_Solver=picomus  $Fcnf $file > $Fwit-mh-mus
  else
      echo "$PY -t 7200 -v4 -TT_PYSAT -q -mh -check_compact $Fcnf $file"
      $PY -t 7200  -v4 -TT_PYSAT -check_compact -q -mh  $Fcnf $file > $Fwit-mh
  fi

done
}

#first_witness
# for each of the dir in $1 to compute minimal witness 
for dir in `ls $1`
do
  for i in 0 1 
  do
     second_witness `pwd`/$1/$dir  $i 2>&1  > `pwd`/$1/$dir/witness-$i-mh.txt&
  done
done
