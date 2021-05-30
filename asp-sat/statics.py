import numpy as np
import glob
import os
import sys

def solved(lines, instance): 
   # return 1: if the instance is solved according to wit_lines, which is a list of lines from the witness
   # 	    2: if the instance is unsatisfiable
   # 	    3: if the instance is out of time, the next line is not invalid model
   for i in range(len(lines)):
      if lines[i].find(instance) >= 0 and i < len(lines)-1:
          if lines[i+1].find('YES') >=0 : return 1
          if lines[i+1].find('invalid') or lines[i+1].find('Unknown') >=0: return 2
   return 3

def one_dir(lp_cnf=0, type=0):
# compute the 1-8) for the _directory _dir
   # lp_cnf 0: for logic program, 1 for cnf theory
   # type =0: without MUS solver
   # type = 1: with MUS solver

   theory_model = [['lp', 'm'], ['cnf', 'm-m']]
   _instances = glob.glob( '*.' + theory_model[lp_cnf][0] ) 
   _models = [s.replace('.' + theory_model[lp_cnf][0], '.' + theory_model[lp_cnf][1]) for s in _instances]
   #_models= glob.glob( '*.' + theory_model[lp_cnf][1] )

   f_wit = open('wit-'+str(type) + '.txt', 'r')
   wit_lines = f_wit.readlines()
   f_wit.close()


   metrics = [.0, .0]
   for i in range(len(_instances)): #_theory in _instances:
      if solved(wit_lines, _instances[i]) == 1:      
          metrics[0] +=  os.path.getsize(_instances[i])
          metrics[1] +=  os.path.getsize(_models[i]) 

   n_select = len(_instances)
   n_unsat = int (os.popen('grep ^UNSAT *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_unknown = int( os.popen('grep ^UNKNOWN  *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_solved = int( os.popen('grep Time wit-' + str(type) + '.txt | wc -l').read().split()[0])
   n_sat   = n_select - n_unsat - n_unknown
   n_compact = int (os.popen('grep True  wit-' + str(type) + '.txt | wc -l').read().split()[0])
   #n_tm_out = # the same as memory out
   
   time, mem, clauses = .0, .0, [0,0,0]
   _time = os.popen('grep Time wit-' + str(type) + '.txt').read().split('\n')
   _mem = os.popen('grep Memory wit-' + str(type) + '.txt').read().split('\n')
   _clauses = os.popen('grep head\>2 wit-' + str(type) + '.txt').read().split('\n')

   for i in range(len(_time)-1):
        time += float(_time[i].split()[1])
        mem += float(_mem[i].split()[1])
        clauses[0] += int(_clauses[i].split()[0])
        clauses[1] += int(_clauses[i].split()[1])
        clauses[2] += int(_clauses[i].split()[2])
   if n_solved > 0:
       metrics[0] = metrics[0]  / n_solved / 1024 / 1024 # in MB
       metrics[1] = metrics[1]  / n_solved / 1024  # in KB 
       time /= n_solved
       mem  /= n_solved
       for i in range(3):
           clauses[i] /= n_solved
   return n_select, n_sat, n_unsat, n_solved, metrics[0], metrics[1], time, mem, clauses[0], clauses[1], clauses[2], n_compact

if __name__ == "__main__":
   
   '''# to compute 
    1) |selected| the number instances selected from all the instances (SAT: == |total|, ASP: <=|total|)
    2) |sat| the number of satisfiable benchmarks instance (in 2 hours)
    2.5) |unsat| the number of unsatisfiable benchmarks instance (in 2 hours)

       1) and 2) are computed by find .lp and .m (.cnf and .m-m respectively)
    3) |solved| minimal witness is computed in 2 hours
       These three can put together as /total/sat(2)/solved(2)

       The followin are all in average of solved intances
    4) |\Sigma| the size of solved instances (logic program or cnf theory)
    5) |M|      the size of the minimal model 
    6) Time:    cpu time 
    7) Mem:     mem 
    8) |\Pi|a:  the number of atoms with more than one clauses in its witness
       |\Pi|2:  the number clauses with more than one positive atoms in its witness
       |\Pi|t:  the size of the witness for this kind of atom

       3-8) are computed from wit-0.txt (without mus solver) and wit-1.txt (with mus solver)

   '''
   _dtype = ('asp', 'sat')
   print("|select| |sat| |unsat| |solved| |Sigma|(M) |Model|(K) CPU(s) MEM (M)  |atom-2|  |clauses-2| |clauses| |compact|")
   for _d in range(len(_dtype)):
       
       dirs = os.popen('ls '+_dtype[_d]).read().split()
       for dclass in dirs:
          os.chdir(_dtype[_d]+"/"+dclass)
          print(dclass)
          for i in one_dir(lp_cnf=_d, type=0):
              if type(i) == int:
                  print("{:<6} ".format(i), end='')
              else: # float
                  print("%.4f "%i, end='')
          print("\n")
          for i in one_dir(lp_cnf=_d, type=1):
              if type(i) == int:
                  print("{:<6} ".format(i), end='')
              else: # float
                  print("%.4f "%i, end='')
          print("\n")
          #print("{0} \n {1}\n".format(dclass, one_dir(lp_cnf=_d, type=0)))
          #print("    {0}\n".format(dclass, one_dir(lp_cnf=_d, type=1)))
          os.chdir("../../")
       print("\n")
