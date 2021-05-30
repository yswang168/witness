#!/bin/bash


function wit_dir()
{
# the directory
PY="python3.7 cb_witness.py"

dir=$1
## $4=m-m or $4=m for cnf and lp repectively
## $3=cnf  or $3=lp
$3=cnf
$4=m-m
echo $3 $4
for file in "`ls ${dir}/*.`$3" #cat ${dirs}/SAT`
do
#  if [ -e ${file/.m/\.wit} ]; then
#    continue
#  fi
  Mlp=$file #${dirs}"/"${file}
  RES="`grep UNSAT $Mlp`"
  if [ ! -z $RES ]; then
    continue
  fi
  RES="`grep UNKNOWN $Mlp`"
  if [ ! -z $RES ]; then
    continue
  fi
  Flp="${Mlp/\.$3/\.$4}"
  Fwit="${Mlp/\.$3/\.wit}"

  if [[ $# -ge 4 && $2 -eq 1 ]];
   then
      echo "$PY -t 7200 -v4 -TT_PYSAT -lp  -q -mh -MUS_Solver=picomus -check_compact  $Flp $Mlp"
      $PY -t 7200  -v4 -TT_PYSAT -lp -check_compact  -q -mh -MUS_Solver=picomus  $Flp $Mlp > $Fwit-mh-mus
  else
      echo "$PY -t 7200 -v4 -TT_PYSAT -lp -q -mh -check_compact  $Flp $Mlp"
      $PY -t 7200  -v4 -TT_PYSAT -lp -check_compact -q -mh   $Flp $Mlp > $Fwit-mh
  fi

done
}


#first_witness
# for each of the dir in $1 to compute minimal witness
for dir in `ls $1`
do
  for i in 0 1
  do
     wit_dir `pwd`/$1/$dir  $i $2 $3  #> `pwd`/$1/$dir/witness-$i-q.txt 2> `pwd`/$1/$dir/witness-$i-q-err.txt &
  done
done

