# -*- coding: UTF-8 -*-
import subprocess
import argparse
from generate_theory import generate_theory
from min_model import get_min_model
#  get_min_model(File, SAT_SOLVER="cadical", TEMP_CNF = ".TEMP_CNF_", time_out=1800):
import os,sys
import random
import re
import math
from run import to_dimacs
import time

TEMP_THEORY = ".TEMP_THEORY_WORST_"
TEMP_MODEL  = ".TEMP_MODEL_WORST_" 
OUT_PUT = "OUT_PUT_WORST_"
time_out = 1800

def build_worst_clauses(n,m=1,cycle=False):
    clauses = []
    for j in range(m):
        c_p = j*n
        neg = set()
        for i in range(2,n+1):
            if j > 0:
                neg = set([ i + (j-1)*n for i in range(1,n+1) ])
            if cycle and j==0: # for cycle case
                clauses.append((set([1 + c_p]),set([i + c_p]).union(set([x]))))
                clauses.append((set([1 + c_p]),set([i + c_p]).union(set([y]))))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(set([x]))))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(set([y]))))
            else:
                clauses.append((set([1 + c_p]),set([i + c_p]).union(neg)))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(neg)))
        if cycle and j == 0: # for cycle case
            clauses.append((set([i + c_p for i in range(2,n+1)]),set([x])))
            clauses.append((set([i + c_p for i in range(2,n+1)]),set([y])))
        else:
            clauses.append((set([i + c_p for i in range(2,n+1)]),neg))
    if cycle:
        clauses.append((set([x,y]), set()))
        clauses.append((set([y]), set([i + c_p for i in range(1,n+1)])))
        clauses.append((set([x]), set([i + c_p for i in range(1,n+1)])))
    model = set([i for i in range(1, n*m+1)])
    if cycle:
        model = model.union(set([x,y]))

    return clauses, model

def get_mm_worstcase(n,m=1, cycle=False):

    # build the claues
    clauses = []
    Yes = False
    nc = 0 
    '''
    for j in range(m):
        for i in range(2,n+1):
            c_p = j*n
            neg = set()
            if j > 1:
                neg = set([ i + (j-1)*n for i in range(1,n+1) ])
            clauses.append((set([1 + c_p]),set([i + c_p]).union(neg)))
            nc += 1
            clauses.append((set([i + c_p]),set([1 + c_p]).union(neg)))
            nc +=1
        clauses.append((set([i + c_p for i in range(2,n+1)]),neg))
        nc += 1
    '''
    clauses, model = build_worst_clauses(n, m=m, cycle=cycle)
    # wirte the clause into CNF file

    _file = ".worst_mm_"+str(os.getpid())+".cnf"
    _fs = open(_file, "w")
    strs = to_dimacs(clauses, len(model), len(clauses))

    _fs.write(strs)
    _fs.close()
    # get a minimal model by cadical

    s1 = time.time()
    res = get_min_model(_file, nc = len(clauses))
    seconds = time.time() - s1

    os.remove(_file)
    if  (res == None or res == -1):
        return False, seconds
    else:
        return True, seconds
    

def checkMin_worstcase(n,m=1, cycle=False):
    clauses = []
    Yes = False
    '''
    for i in range(2,n+1):
        clauses.append((set([1]),set([i])))
        clauses.append((set([i]),set([1])))
    clauses.append((set([i for i in range(2,n+1)]),set()))
    for j in range(m):
        for i in range(2,n+1):
            c_p = j*n
            neg = set()
            if j > 1:
                neg = set([ i + (j-1)*n for i in range(1,n+1) ])
            clauses.append((set([1 + c_p]),set([i + c_p]).union(neg)))
            clauses.append((set([i + c_p]),set([1 + c_p]).union(neg)))
        clauses.append((set([i + c_p for i in range(2,n+1)]),neg))


    model = set([i for i in range(1, n+1)])
    '''
    clauses, model = build_worst_clauses(n, m=m, cycle=cycle)
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    with open(TEMP_THEORY, 'w') as f:
        f.write(to_dimacs(clauses, len(model), len(clauses)))
    out = subprocess.check_output(["python3.7", "check_min.py", "-TT_PYSAT",TEMP_THEORY, TEMP_MODEL]).decode("ascii")
    os.system("cp "+TEMP_THEORY +" " + TEMP_MODEL + " /tmp")
    
    if out.find("YES") != -1:
        Yes = True
    return (Yes, float(out.split("\n")[0]))
'''
def cbwitness_worstcase(n):
    clauses = []
    Yes = False
    for i in range(2,n+1):
        clauses.append((set([1]),set([i])))
        clauses.append((set([i]),set([1])))
    clauses.append((set([i for i in range(2,n+1)]),set()))
    model = set([i for i in range(1, n+1)])
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    with open(TEMP_THEORY, 'w') as f:
        f.write(to_dimacs(clauses, n, n))
    os.system("cp "+TEMP_THEORY +" " + TEMP_MODEL + " /tmp")
    try:
        #out = subprocess.check_output(["python3.7", "cb_witness.py", "-q", "-v4", "-TT_PYSAT", "-MUS_Solver=picomus", TEMP_THEORY, TEMP_MODEL], timeout=time_out).decode("ascii")
        out = subprocess.check_output(["python3.7", "cb_witness.py", "-q", "-v4", "-TT_PYSAT",  TEMP_THEORY, TEMP_MODEL], timeout=time_out).decode("ascii")
    except subprocess.TimeoutExpired as e:
        return -1
    if out.find("YES") != -1:
        Yes = True
    #print(out)
    return (Yes, float(out.split("\n")[2].split(" ")[1]))
'''
def cbwitness_worstcase(n, m=1, MUS=True, cycle=False):
    # n: the number of atoms
    # m: the number of cascades
    ##### for cycle case
    x = n*m + 1
    y = x + 1
    xy = set([x, y])
    #####
    clauses = []
    Yes = False
    for j in range(m):
        c_p = j*n
        neg = set()
        for i in range(2,n+1):
            if j > 0:
                neg = set([ i + (j-1)*n for i in range(1,n+1) ])
            if cycle and j==0: # for cycle case
                clauses.append((set([1 + c_p]),set([i + c_p]).union(set([x]))))
                clauses.append((set([1 + c_p]),set([i + c_p]).union(set([y]))))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(set([x]))))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(set([y]))))
            else:
                clauses.append((set([1 + c_p]),set([i + c_p]).union(neg)))
                clauses.append((set([i + c_p]),set([1 + c_p]).union(neg)))
        if cycle and j == 0: # for cycle case
            clauses.append((set([i + c_p for i in range(2,n+1)]),set([x])))
            clauses.append((set([i + c_p for i in range(2,n+1)]),set([y])))
        else:
            clauses.append((set([i + c_p for i in range(2,n+1)]),neg))
    if cycle:
        clauses.append((set([x,y]), set()))
        clauses.append((set([y]), set([i + c_p for i in range(1,n+1)])))
        clauses.append((set([x]), set([i + c_p for i in range(1,n+1)])))
    model = set([i for i in range(1, n*m+1)])
    if cycle:
        model = model.union(set([x,y]))

    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    with open(TEMP_THEORY, 'w') as f:
        f.write(to_dimacs(clauses, n, n))
    os.system("cp "+TEMP_THEORY +" " + TEMP_MODEL + " /tmp")
    try:
        if MUS:
           out = subprocess.check_output(["python3.7", "cb_witness.py", "-q", "-v4", "-TT_PYSAT", "-check_compact", "-MUS_Solver=picomus", TEMP_THEORY, TEMP_MODEL], timeout=time_out).decode("ascii")
        else:
           out = subprocess.check_output(["python3.7", "cb_witness.py", "-q", "-check_compact", "-v4", "-TT_PYSAT",  TEMP_THEORY, TEMP_MODEL], timeout=time_out).decode("ascii")
    except subprocess.TimeoutExpired as e:
        return (Yes,-1.0)
    if out.find("YES") != -1:
        Yes = True
    #print(out)
    return (Yes, float(out.split("\n")[2].split(" ")[1]), out.split("\n")[1].split(" ")[:3])

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Run test')
    parser.add_argument("lower", type=int, default=1, help = "The lower bound of number of atoms")
    parser.add_argument("upper", type=int, default=1, help = "The upper bound of number of atoms")
    parser.add_argument("-m", type=int, default=1, help = "The number of cascades")
    parser.add_argument("-mm", action='store_true', help = "Computing the minimal model")
    parser.add_argument("-cycle", action='store_true', help = "The theory is cycle")
    parser.add_argument("-mc", action='store_true', help = "Whether do minimal model checking")
    parser.add_argument("-MUS", action='store_true', help = "Whether using MUS picomus")

    args = parser.parse_args()


    mc = args.mc
    MUS = args.MUS
    lower = args.lower
    upper = args.upper
    m = args.m
    OUT_PUT = OUT_PUT +  str(lower) +"_"+ str(upper)+ "_" + str(m) + "_"

    TEMP_THEORY += str(os.getpid())
    TEMP_MODEL  += str(os.getpid()) 
    OUT_PUT += str(os.getpid())

    os.system("echo n	time > " + OUT_PUT)
    for n in range(lower, upper+1, 10):
        if args.mm:
            Yes, _time = get_mm_worstcase(n,m=m)
            s = str(n) + "	" + str(round(_time,6))
            os.system("echo " + s + str(Yes) + "  >> " + OUT_PUT )
            print("{0} {1:6f} {2}".format(n,_time,str(Yes)))
            
            continue
        if not mc:
            Yes, _time, _nac = cbwitness_worstcase(n,m=m,MUS=MUS, cycle=args.cycle) 
            s = str(n) + "	" + str(round(_time,6))
            os.system("echo " + s + str(Yes) + "  >> " + OUT_PUT )
            print("{0} {1:6f} {2} {3}".format(n,_time,str(Yes)," ".join(_nac)))
        else:
            Yes, _time = checkMin_worstcase(n,m=m)
            s = str(n) + "	" + str(round(_time,6))
            os.system("echo " + s + str(Yes) + " >> " + OUT_PUT)
            print("{0} {1:6f} {2}".format(n, _time, str(Yes)))

        os.remove(TEMP_THEORY)
        os.remove(TEMP_MODEL)

