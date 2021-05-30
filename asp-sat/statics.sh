#! /bin/bash

# statics the average time, memory and clauses with more than two positive literals in the derivation

# usage
# $0 FILE

function asp_sat()
{
tc=0
mc=0
nHC=(0 0 0)
grep clauses $1 | cut -f 1,2,3 -d" " > /tmp/$$

while read nc 
do
  #echo $nc
  #Nc=(${nc/ / /})
  Nc=($nc)
  i=0
  while [ $i -lt ${#Nc[@]} ]
  do
    let nHC[$i]=${nHC[$i]}+${Nc[$i]}  
    let i=$i+1
  done
  #let ac=$ac+$nc
done <  /tmp/$$ 

grep Time $1 | cut -f 2 -d" " > /tmp/$$.t
while read time
do
  tc=`echo "scale=4; $tc+$time"|bc`
done </tmp/$$.t

grep Memory $1 | cut -f 2 -d " " > /tmp/$$.m
while read mem
do
  mc=`echo "scale=4; $mc+$mem"|bc`
done </tmp/$$.m

num=`wc -l /tmp/$$ | cut -f 1 -d" "`
tc=`echo "scale=2; $tc/$num"|bc`
mc=`echo "scale=2; $mc/$num"|bc`
i=0
while [ $i -lt ${#Nc[@]} ]
do
  nHC[$i]=`echo "scale=2; ${nHC[$i]}/$num"|bc`
  let i=$i+1
done
#ac=`echo "scale=2; $ac/$num"|bc`

echo 'A-time(s) A-memory(M) A-atoms A2-clauses A-clauses'
echo $tc $mc $ac ${nHC[@]}

rm -fr /tmp/$$.*
}

function dirs_st()
{
declare types
types=(lp cnf)
mnames=(m m-m)
_type=$2  #the type 0: logic program, 1: cnf theory
dir=$1
_mus=$3 # 0: without mus solver, 1: with mus solver

dirs=`ls $dir`
for sub_dir in $dirs
do
  s_dir=$dir\\$sub_dir
  # number of tested instance
  n_test=`ll $s_dir\*.${types[$2]} | wc -l`
  # number of UNSAT
  n_unsat=`grep ^UNSAT $s_dir\*.${mnames[$2]} | wc -l`
  let n_sat=$n_test-$n_unsat
  
  n_solved=`grep YES $s_sir\wit-$mus.txt | wc -l`
  n_model_mem=
  n_theory_mem=
  n_test=`ll $dir\$as\*.lp | wc -l`

done
}


dirs_st sat 1
dirs_st asp 0


