### Compute a minimal model of clauses in DIMACS
### Yisong Wang
### 2019-08-20

# -*- coding: UTF-8 -*-
import argparse
import resource
import subprocess 
import os,sys
import random
import re 
from pysat.formula import CNF
from pysat.solvers import Solver
'''
SAT_SOLVER = "cadical"   # Cadical sr2019
TEMP_CNF   = ".TEMP_CNF_"
NUM_CLAUSES = 0
time_out = 1800
'''
def get_a_model(File, SAT_SOLVER="cadical", time_out=1800):
    if (SAT_SOLVER == "cadical"):
        try: 
            res = subprocess.check_output([SAT_SOLVER, "-q", File],timeout=time_out).decode("ascii")     
        except subprocess.CalledProcessError as e:
            res = str(e.output)
            res = res.strip("b'") 
            pass
        except subprocess.TimeoutExpired as t:
            return None
        if res.find("UNSATISFIABLE") != -1:
            return -1 # for UNSAT
        res = res.replace("s SATISFIABLE",'')	
        res = res.replace("\\n", '')
        res = res.replace('v', '')
        res = res.strip()
    else: # minimal model solver MRSAT
        try:
            res = subprocess.check_output(["minimal", "-verb=0", File],timeout=time_out).decode("ascii")
        except subprocess.CalledProcessError as e:
            res = str(e.output)
            res = res.strip("b'")
            pass
        except subprocess.TimeoutExpired as t:
            return None
        if res.find("UNSATISFIABLE") != -1:
            return -1
        if res.find("SATISFIABLE") != -1:
            model = res.split("\n")[7].strip("[]");
            return model
    return res

def build_up_CNF_model(File, n_clauses:int, model_:str, TEMP_CNF:str):
    model = list(map(int, model_.split(' ')))
    negative = list(filter(lambda x: x<0, model))
    positive = list(filter(lambda x: x>0, model))

    with open(TEMP_CNF, "w") as f:
        f.write("p cnf "+str(len(model)-1)+ " "+ str(len(negative)+1+n_clauses) + "\n")
        f.write(" ".join(str(-x) for x in positive) + " 0\n")
        for i in range(len(negative)):
            f.write(str(negative[i]) + " 0\n")
        with open(File, "r") as sf:
            lines = sf.read().split('\n')
            for j in range(len(lines)):
                if lines[j].find("p ") != -1 or lines[j].find("c ") != -1:
                    continue
                f.write(lines[j] + "\n")
        f.close()
        sf.close()
        return positive

def get_min_model(File, SAT_SOLVER="cadical", TEMP_CNF = ".TEMP_CNF_", time_out=1800, nc=None):  
	# compute a minimal model of File (in CNF)
	# return None if UNSAT
	# a minimal model otherwise 
    TEMP_CNF += str(os.getpid())
    NUM_CLAUSES = None
    if nc != None:
        NUM_CLAUSES = nc
    else:
        with open(File) as f:
            lines = f.read().split('\n')
            for i in range(10):
                if lines[i].find("p cnf") != -1:  # get the number of clauses in "p cnf K C", we assume the first line 
                   NUM_CLAUSES = int(lines[i].split(' ')[3])
                   break

    res = get_a_model(File, SAT_SOLVER, time_out)
    if res == None or res == -1:
        return res
    #if SAT_SOLVER == 'minimal': # get the minimal model by minimal
    #    return list(map(int, res.split(" ")))


    keep_model = build_up_CNF_model(File, NUM_CLAUSES, res, TEMP_CNF)
	# build up the new theory by adding new clauses into File
    while(True):
        res = get_a_model(TEMP_CNF, SAT_SOLVER, time_out)
        if  res == -1:
            return keep_model
        if  res == None: return None
        keep_model = build_up_CNF_model(File, NUM_CLAUSES, res, TEMP_CNF)

    try:
        os.remove(TEMP_CNF)
    except:
        pass


if __name__ == "__main__":
	# usage %0 <input>
    # Sat sovler name cae be
    '''
    cadical     = ('cd', 'cdl', 'cadical')
    glucose3    = ('g3', 'g30', 'glucose3', 'glucose30')
    glucose4    = ('g4', 'g41', 'glucose4', 'glucose41')
    lingeling   = ('lgl', 'lingeling')
    maplechrono = ('mcb', 'chrono', 'maplechrono')
    maplecm     = ('mcm', 'maplecm')
    maplesat    = ('mpl', 'maple', 'maplesat')
    minicard    = ('mc', 'mcard', 'minicard')
    minisat22   = ('m22', 'msat22', 'minisat22')
    minisatgh   = ('mgh', 'msat-gh', 'minisat-gh')
    '''
    parser = argparse.ArgumentParser(description='Run min_model, computing a minimal model of a cnf')
    parser.add_argument("-p", help="Using PYSAT package", action='store_true',default=False,dest="bPySat")
    parser.add_argument("CNF_file", help = "theory file")
    parser.add_argument("-solver", help = "SAT solver", dest="solver", default="cadical")
    args = parser.parse_args()
    bPySat = args.bPySat
    CNF_file=args.CNF_file
    solver_name=args.solver
    resource.setrlimit(resource.RLIMIT_CPU,(7200,7200))
    if not bPySat:
        print(get_min_model(sys.argv[1], SAT_SOLVER=solver_name,time_out=0))
    else: 
        formula = CNF(CNF_file)
        s = Solver(name=solver_name)
        s.append_formula(formula.clauses)
        if not s.solve(): 
            print("UNSAT")
            sys.exit(1) # no minimal model, UNSAT
        M = s.get_model()
        s.add_clause([-x for x in filter(lambda x: x > 0,  M)])
        for x in M:
            if x < 0:
                s.add_clause([x])
        while( s.solve() ):
            M = s.get_model()
            s.add_clause([-x for x in filter(lambda x: x > 0,  M)])
            for x in M:
                if x < 0:
                    s.add_clause([x])
        print([x for x in filter(lambda x: x>0, M)])
