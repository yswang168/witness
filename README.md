# Computing minimal beta-witness


# python3.7 cb_witness.py --help
### usage: cb_witness.py [-h] [-file_S FILE_S] [-MUS_Solver MUS_SOLVER]  (-TT_OLD | -TT_SAT | -TT_PYSAT) (-orig | -v2 | -v3 | -v4) [-WITNESS_OLD] [-REDUCE] [-lp] [-q] [-t MCT] [-mh]  [-check_compact] 	file_CNF file_M

## Run cbwitness

## positional arguments:
  	file_CNF              theory file
  	file_M                model file

## optional arguments:
  	-h, --help            show this help message and exit
  	-file_S FILE_S        S file
  	-MUS_Solver MUS_SOLVER MUS solver
  	-TT_OLD               use enumeration algorithm for consequence checking
  	-TT_SAT               use sat solver for consequence checking (large overhead for file generation
  	-TT_PYSAT             use pysat package with glucose4 for consequence checking
  	-orig                 use the original algorithm proposed in the original paper
  	-v2                   use the second version of the algorithm suited for small minimal witnesses
  	-v3                   use the third version of the algorithm just mentioned in the thesis. It first adds clauses to Sigma_v until atoms follow and then removes them until just one atom is the consequence (pair (v,Sigma_v))
  	-v4                   use unit propagation at first in each iteration
  	-WITNESS_OLD          unoptimized version of the algorithm (enumerating over all theory subsets and no theory reducing) Just possible with the original version (-orig argument)
  	-REDUCE               reduce theory every time an atom is added to the set T
  	-lp                   The theory file is a logic program
  	-q                    be quiet
  	-t MCT                CPU limit (s)
  	-mh                   print the rules with multi head atoms after minimal reduct in witness
  	-check_compact        Checking if the witness is compact
