# -*- coding: UTF-8 -*-
import argparse
import glob 
import numpy as np
import subprocess
import os, sys
import random
import re, time
import math
import shutil 
from data.generate_theory import generate_theory
from data.min_model import get_min_model

latex = []
TEMP_THEORY = ".TEMP_THEORY_"
TEMP_MODEL  = ".TEMP_MODEL_"
TEMP_MIN_MODEL = ".TEMP_MIN_MODEL_"
TEMP_DLV = ".TEMP_DLV_"
TEMP_CLASP = ".TEMP_CLASP_"
SAT_INPUT = ".TEMP_SAT_INPUT_"
OUT_PUT = "OUT_PUT_"
OUT_PUT_MIN = "OUT_PUT_MIN_"
ATOM_PRE = "p_"
steps = list()
time_out = 7200 
COMPUT_MINIMAL_MODEL=False #True

### Yisong
def generate_clasp_maps(a:'int'):
    to_dlv_map = {}
    from_dlv_map = {}
    for i in range(1, a+1):
        s = ATOM_PRE + str(i)
        to_dlv_map[i] = s
        from_dlv_map[s] = i
    return (to_dlv_map, from_dlv_map)

def to_clasp(clauses, to_clasp_map):
    strings = []
    for head, body in clauses:
        strings.append(" | ".join(to_clasp_map[atom] for atom in head))
        if len(body) > 0:
            strings.append(" :- ")
            strings.append(" , ".join(to_clasp_map[atom] for atom in body))
        strings.append(".\n")
    return ''.join(strings)

def get_clasp_minmodel(clauses, ATOMS):
    to_clasp_map, from_clasp_map = generate_clasp_maps(ATOMS)
    clasp = to_clasp(clauses, to_clasp_map)
    with open(TEMP_CLASP, 'w') as f:
        f.write(clasp)
        f.close()
    line = None 
     
    try:
       line = subprocess.check_output(["clingo", "--models=1", "--verbose=0", "--quiet=1", "--warn=no-atom-undefined", TEMP_CLASP],timeout=time_out).decode("ascii") 
    except subprocess.TimeoutExpired as e: 
        return None
    except subprocess.CalledProcessError as e:
        line = str(e.output)
        if line.find("UNSATISFIABLE") != -1: return -1
        line = line.strip("b'").split("\\")[0] 
    if line == "" or line == None :
        return None ## no answer set
    else: 
        return [from_clasp_map[x.strip(" ")] for x in filter(None, line.split(" "))]
        #return [from_clasp_map[x.strip(" ")] for x in filter(None, line.strip("}{\n\r").split(","))]
### ----------------------

def generate_dlv_maps(a):
    to_dlv_map = {}
    from_dlv_map = {}
    for i in range(1, a+1):
        x = i
        s = ""
        while x > 0:
            s += chr(x%26 + ord('a'))
            x//=26
        to_dlv_map[i] = s
        from_dlv_map[s] = i
    return (to_dlv_map, from_dlv_map)

def to_dlv(clauses, to_dlv_map):
    strings = []
    for head, body in clauses:
        strings.append(" v ".join(to_dlv_map[atom] for atom in head))
        strings.append(" :- ")
        strings.append(" , ".join(to_dlv_map[atom] for atom in body))
        strings.append(".\n")
    return ''.join(strings)

def to_dimacs(clauses, ATOMS, CLAUSES):
    strings = []
    strings.append("c average clause length: {0}".format(sum(len(x[0])+len(x[1]) for x in clauses) / len(clauses)))
    strings.append("\n")
    strings.append("c average head length: {0}".format(sum(len(x[0]) for x in clauses) / len(clauses)))
    strings.append("\n")
    strings.append("p cnf {0} {1}".format(ATOMS, CLAUSES))
    strings.append("\n")

    for head, body in clauses:
        for atom in head:
            strings.append(str(atom))
            strings.append(" ")
        for atom in body:
            strings.append(str(-atom))
            strings.append(" ")
        strings.append("0\n")
    return ''.join(strings)

def generate_sat_input(clauses, ATOMS, CLAUSES, minmodels=None):
    satinput = [to_dimacs(clauses, ATOMS, CLAUSES)]
    all_atoms = set([x for x in range(1, ATOMS+1)])
    i = 0
    if minmodels == None:
        minmodels = []
    for model in minmodels:
        satinput.append(' '.join([str(-atom) for atom in model]))
        satinput.append(' ')
        leftatoms = all_atoms.difference(set(model))
        satinput.append(' '.join([str(atom) for atom in leftatoms]))
        satinput.append(' 0\n')
        i += 1
    satinput[0] = re.sub("p cnf .*\n", "p cnf {0} {1}\n".format(ATOMS, CLAUSES+i), satinput[0])
    return ''.join(satinput)

def calcminmodels(clauses, ATOMS):
    to_dlv_map, from_dlv_map = generate_dlv_maps(ATOMS)
    dlv = to_dlv(clauses, to_dlv_map)
    with open(TEMP_DLV, 'w') as f:
        f.write(dlv)
    dlvout = subprocess.check_output(["dlv", "-silent", TEMP_DLV],timeout=time_out).decode("ascii")
    minmodels = []
    for line in dlvout.strip().split("\n"):
        if line == "":
            break
        minmodels.append([from_dlv_map[x.strip(" ")] for x in filter(None, line.strip("}{\n\r").split(","))])
        if len(minmodels) == 0:
            continue
    return minmodels

def generate_tempmodel(satinput):
    with open(SAT_INPUT, 'w') as f:
            f.write(''.join(satinput))
    try:
        # weird exit status
        subprocess.check_output(["minisat", SAT_INPUT, TEMP_MODEL],timeout=time_out)
    except subprocess.CalledProcessError as e:
        pass
    except subprocess.TimeoutExpired as t:
        return None
    with open(TEMP_MODEL, 'r') as f:
        model = f.read().replace('\n', '')
        #print(model)
    if "UNSAT" in model:
        # we want theories with models that do not have minimal models            
        return "UNSAT"
    model = model.replace("SAT", "")
    model = [int(x) for x in model.split() if int(x) > 0]
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    return model

def checkMin_worstcase(n):
    clauses = []
    for i in range(1,n):
        clauses.append((set([i]),set([i+1])))
    clauses.append((set([n]), set([1])))
    model = set([i for i in range(1, n+1)])
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    with open(TEMP_THEORY, 'w') as f:
        f.write(to_dimacs(clauses, n, n))
    out = subprocess.check_output(["python3.7", "check_min.py", TEMP_THEORY, TEMP_MODEL]).decode("ascii")
    return float(out.split("\n")[0])

def cbwitness_worstcase(n):
    clauses = []
    for i in range(2,n+1):
        clauses.append((set([1]),set([i])))
        clauses.append((set([i]),set([1])))
    clauses.append((set([i for i in range(2,n+1)]),set()))
    model = set([i for i in range(1, n+1)])
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    with open(TEMP_THEORY, 'w') as f:
        f.write(to_dimacs(clauses, n, n))
    out = subprocess.check_output(["python3.7", "cb_witness.py", "-v2", TEMP_THEORY, TEMP_MODEL]).decode("ascii")
    #print(out)
    return float(out.split("\n")[0])
    
def get_random_minmodel(clauses, ATOMS):
    to_dlv_map, from_dlv_map = generate_dlv_maps(ATOMS)
    dlv = to_dlv(clauses, to_dlv_map)
    with open(TEMP_DLV, 'w') as f:
        f.write(dlv)
    try:
        dlvout = subprocess.check_output(["dlv", "-n=1", "-silent", TEMP_DLV],timeout=time_out).decode("ascii") ### Yisong, change for linux
    except subprocess.TimeoutExpired as e:
        return None

    line = dlvout
    if line == "": ## no answer set
        return -1 
    else:
        return [from_dlv_map[x.strip(" ")] for x in filter(None, line.strip("}{\n\r").split(","))]

#  compute a minimal model by minimal reduct (Algorithm 3 in TOCL, i.e. MMSAT -mod=MRSAT cnf_file)
'''
Its output looks like:
WARNING: for repeatability, setting FPU to use double precision
Memory used           : 19.50 MB
CPU time              : 0.010552 s
ComputeModelCount     : 1
CheckModelCount       : 1
ComputeMIniModelCount : 10
SATISFIABLE
[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 ]
'''
def get_minimal_model_MR(CNF, mr=False):
    # mr=False, does not use minimal reduct when update new theores 
    # mr=True,  use minimal reduct when update the new theory
    try:
        if mr:
           line = subprocess.check_output(["mr_minimal", "-mod=MRSAT", CNF], timeout=time_out).decode("ascii")
        else:
           line = subprocess.check_output(["mr_minimal", "-mod=MMSAT", CNF],timeout=time_out).decode("ascii")
    except subprocess.TimeoutExpired as e:
        return None
    
    if line.find("UNSATISFIABLE") != -1: return None

    lines = line.split("\n")
    model = lines[len(lines)-1] #get the mininimal model
    model = model.strip("[]").split()
    model = [int (a) for a in model]
    
    return model

# test the minimal model computing cost for 3CNF by minimal_model (algorithm 3), cadical (a trivial procedure, clingo, dlv)
def test_v5(na:'number of atoms', cl=3):
    steps = np.array(range(30,51,1))
    for ratio in steps:
        nc = int(ratio / 10.0 * na)
        times = 20
        sec = 0.0
        s  = [0.0]*5
        unsat_times = 0
        timeouts = [0]*5
        while times > 0:
            clauses = generate_theory(nc, na, cl, hp='UNIFORM', cl_std_derivation=0)
            satinput = generate_sat_input(clauses, na, nc)
               
            T_File = ".TEMP_SAT_FILE_" + str(os.getpid())
            with open(T_File,"w") as f:
                f.write(satinput)
                f.close()
            sec = time.time()
            minmodel = get_min_model(T_File) #,SAT_SOLVER="minimal")  # by cadical in default

            if minmodel == -1:
                unsat_times += 1
                continue
            if minmodel == None:
                timeouts[0] += 1
                continue

            s[0] += time.time()-sec
            sec = time.time()
            minmodel = get_minimal_model_MR(T_File) # by mr_minimal, using minimal reduct when update the theory
            #assert minmodel != None, "MMSAT error."
            s[1] += time.time() - sec
            if minmodel == None:
                timeouts[1] += 1


            sec = time.time()
            minmodel = get_minimal_model_MR(T_File, mr=True) # by MMSAT, does not use minimal reduct when update the theory
            #assert minmodel != None, "mr_minimal error."
            s[4] += time.time()-sec
            if minmodel == None:
                timeouts[4] += 1

            os.remove(T_File)

            sec = time.time()
            minmodel = get_clasp_minmodel(clauses, na)  # by clingo
            #assert minmodel != None, 'clingo error.'
            s[2] += time.time() - sec
            if minmodel == None:
                timeouts[2] += 1

            sec = time.time()
            minmodel = get_random_minmodel(clauses, na) # by dlv
            #assert minmodel != None, 'dlv error.'
            s[3] += time.time() - sec
            if minmodel == None:
                timeouts[3] += 1

            times -= 1
        # print the time for cadical mr_minimal clingo dlv and mr_minimal(with minimal reduct for updating theory T) unsat_times
        print("%d %.2f "%(na,ratio/10.0),end='')
        for i in range(5):
            print("%.4f %d "%(s[i]/20, timeouts[i]), end='')
        print("%d"%unsat_times)
  
# add a test for computing minimal model for comparison
# minimal, dlv, clingo


def test_v4(CLAUSES, ATOMS, CLAUSE_LENGTH, HEAD_PROPORTION, fixclauselen = False, MIN_MODEL=0, MIN_CHECK=False, bMUS=True,
             save_model=False, mh=False, _pdir=""):
    # MIN_MODEL = 0 : cadical
    # MIN_MODEL = 1 : clasp
    # MIN_MODEL = 2 : dlv
    # MIN_CHECK: do minimal model checking or nor
    global TEMP_MIN_MODEL, TEMP_THEORY

    sum_time1 = 0.0 
    sum_time2 = 0.0
    NON_MIN_MODEL = 0
    sum_minmodlen = 0
    t = 20
    tinitial = t
    out_of_times = 0 ### Yisong
    compact_witnesses = 0 # the total number non-compact witnesss
    sat_dlv_out_of_times = 0
    if COMPUT_MINIMAL_MODEL:
        check_mm = 20
    else:
        check_mm = 0

    head_2, n_clause_2, n_clauses = 0.0, .0, .0 # the number of atoms, clauses_2, clauses with more than one clauses in its witness
    ration =  round(CLAUSES / ATOMS,1)

    while t > 0:   
        _mname = _pdir+"/"+"{:.1f}".format(CLAUSES/ATOMS)+'-'+str(20-t) +"."
        if os.path.exists(_mname+"cnf"): # the clause theory exists
            TEMP_THEORY = _mname + "cnf"
            TEMP_MIN_MODEL = _mname + "m-m"
            if not os.path.exists(_mname+"m-m"): # the minimal mdel of the clause theory exists
                rand_minmodel = get_min_model(TEMP_THEORY)
                with open(TEMP_MIN_MODEL, 'w') as f:
                    f.write(" ".join(str(atom) for atom in rand_minmodel))

        else:
             clauses = generate_theory(CLAUSES, ATOMS, CLAUSE_LENGTH, HEAD_PROPORTION, cl_std_derivation=0)
             minmodels = []
             satinput = generate_sat_input(clauses, ATOMS, CLAUSES, minmodels)
             if MIN_MODEL == 1:
                rand_minmodel = get_clasp_minmodel(clauses, ATOMS)  # by clingo
             elif MIN_MODEL == 2:
                rand_minmodel = get_random_minmodel(clauses, ATOMS) # by dlv
             elif MIN_MODEL == 0: # cadical
                T_File = ".TEMP_SAT_FILE_" + str(os.getpid())
                with open(T_File,"w") as f:
                    f.write(satinput)
                rand_minmodel = get_min_model(T_File) #,SAT_SOLVER="minimal")  # by cadical in default
                os.remove(T_File)
             if rand_minmodel == None: ## out of time limit
                sat_dlv_out_of_times += 1
                continue
             if rand_minmodel == -1: ## unsat
                continue

             sum_minmodlen += len(rand_minmodel)
             if COMPUT_MINIMAL_MODEL: 
                t -= 1
                continue
             if save_model: 
                _mname = _pdir+"/"+"{:.1f}".format(CLAUSES/ATOMS)+'-'+str(20-t) +"."
                TEMP_MIN_MODEL = _mname + "m-m"
                TEMP_THEORY = _mname + "cnf"
                with open(TEMP_MIN_MODEL, 'w') as f:
                     f.write(" ".join(str(atom) for atom in rand_minmodel))
                with open(TEMP_THEORY, 'w') as f:
                     f.write(to_dimacs(clauses, ATOMS, CLAUSES))
        try:
           _command = ["python3.7", "cb_witness.py", "-v4", "-q", "-check_compact", "-TT_PYSAT"]
           if bMUS: _command.append("-MUS_Solver=picomus")
           if mh  : _command.append("-mh")
           _command = _command + [TEMP_THEORY, TEMP_MIN_MODEL]
           out = subprocess.check_output(_command, text=True, timeout=time_out)
        except subprocess.CalledProcessError as e:
           out = e.output
           print(e)
        except TimeoutException as e:
           print("timeout")
           return 
        '''
        The output looks like the below:
	YES
	41:
	   34 -> 25 or 41
	   41 or 34 or 15
	0 0 0 atoms, head>2 clauses, clauses
	Time: 0.094 (s)
	Memory: 13.328 (M)
	The witness is compact: True
        '''
        if save_model: # also save witness
            _fwit = _mname + "wit-mh"
            if bMUS: _fwit = _fwit + "-mus"
            with open(_fwit,"w") as f:
                f.write(out)
        if not "Out of time." in out:
            ##### for debug
            #print(out)
            if not "atoms, head" in out:
               print("something error:")
               print(out)
            _out = out.split("\n") #[2].split(" ")
            #### skip these witness clauses 
            #_k=0
            #while out[_k].find('atoms, head') == -1: _k += 1
            _k = len(_out) - 5 #the last line is empty
            try:
            #if (int(out[len(out)-2]) > 0): # keep this theory and its minimal model
                # os.system("cp "+TEMP_THEORY + " " + TEMP_MIN_MODEL + " /tmp")
                ## just for fun to keep those interesting examples
               head_2 += int(_out[_k].split()[0]) # the number of clauses with head size >= 2.
               n_clause_2 += int(_out[_k].split()[1]) # the number of clauses with head size >= 2.
               n_clauses += int(_out[_k].split()[2]) # the number of clauses with head size >= 2.
               sum_time1 += float(_out[_k+1].split()[1]) # the cpu time 
               if _out[_k+3].split(":")[1].strip() == 'True':
                  compact_witnesses += 1
            except ValueError:
               print(_out[_k+1])
               print(_out)
            except IndexError:
               print(_k+1)
               print(_out)
                #print("got! {0}".format(head_2))
            check_mm += 1 ### checked minimal models
            # 
        else:
            out_of_times += 1
        ## For minimal model checking
        if MIN_CHECK:            
            out = subprocess.check_output(["python3.7", "check_min.py",  "-TT_PYSAT", TEMP_THEORY, TEMP_MIN_MODEL]).decode("ascii")
            out = out.split("\n")
            sum_time2 += float(out[0]) 
            if out[1].find("NO") != -1:
                NON_MIN_MODEL += 1
        t -= 1 

    #w_str_mc = str(k) + " " + str(ration) + " " + str(round(sum_time2/20,6)) + " " + str(NON_MIN_MODEL)
    #os.system("echo "+w_str_mc + " >> " + OUT_PUT_MIN)
    ## latex.append((k, sum_time1/(tinitial-out_of_times), 0, out_of_times)) 
    w_str = str(k) + " " + str(ration) + " " + str(round(sum_time1/check_mm,6)) + " "+ str(sat_dlv_out_of_times) + " " + str(out_of_times) + " " + str(round(head_2/check_mm,3)) + "  " + str(compact_witnesses)
    os.system("echo " + w_str + " >> " + OUT_PUT)
 
    if check_mm > 0:
        print("{0} {1} {2:6f} {3} {4} {5:2f} {6} {7} {8}".format(k, ration, round(sum_time1/check_mm,6),  sat_dlv_out_of_times, out_of_times, round(head_2/check_mm,3), compact_witnesses, n_clause_2, n_clauses))
    else:
        print("{0}  {1:2f} {2} {3} {4} {5:2f} {6} {7} {8}".format(k, ration, 0, sat_dlv_out_of_times, out_of_times,round(head_2/check_mm,3), compact_witnesses, n_clause_2, n_clauses))


def test(CLAUSES, ATOMS, CLAUSE_LENGTH, HEAD_PROPORTION, cb, minmod, k, useminmodels, fixclauselen = False):
    global TEMP_MIN_MODEL, TEMP_THEORY
    sum_time1 = 0
    sum_time2 = 0
    sum_time3 = 0
    sum_modlen = 0
    sum_minmodlen = 0
    t = 20
    tinitial = t
    out_of_times = 0 ### Yisong
    while t>0:   
        # get random theory
        if fixclauselen:
            clauses = generate_theory(CLAUSES, ATOMS, CLAUSE_LENGTH, HEAD_PROPORTION, cl_std_derivation=0)
        else:
            clauses = generate_theory(CLAUSES, ATOMS, CLAUSE_LENGTH, HEAD_PROPORTION)
        
        # generate all minimal models
        minmodels = []
        if useminmodels:
            minmodels = calcminmodels(clauses, ATOMS)
        
        satinput = generate_sat_input(clauses, ATOMS, CLAUSES, minmodels)
        model = generate_tempmodel(satinput)
        if model == "UNSAT":
            continue
        sum_modlen += len(model)
        if minmod or minmod=="BOTH":
            rand_minmodel = get_random_minmodel(clauses, ATOMS)
            sum_minmodlen += len(rand_minmodel)
            with open(TEMP_MIN_MODEL, 'w') as f:
                f.write(" ".join(str(atom) for atom in rand_minmodel))
        with open(TEMP_THEORY, 'w') as f:
            f.write(to_dimacs(clauses, ATOMS, CLAUSES))
 

        #print(' '.join(map(str, filter(lambda x: x>0, atoms))))
        if cb and minmod in (True, "BOTH"):
            out = subprocess.check_output(["python3.7", "cb_witness.py", "-v2", "-TT_OLD", "-REDUCE",  TEMP_THEORY, TEMP_MIN_MODEL]).decode("ascii")
            sum_time1 += float(out.split("\n")[0])
            #print(out)
            assert(out.split("\n")[1] == "YES")
            out = subprocess.check_output(["python3.7", "cb_witness.py", "-v2", "-TT_OLD", TEMP_THEORY, TEMP_MIN_MODEL]).decode("ascii")
            #print(out)
            sum_time2 += float(out.split("\n")[0])

        if not cb and minmod in (True, "BOTH"):
            out = subprocess.check_output(["python3.7", "check_min.py", TEMP_THEORY, TEMP_MIN_MODEL]).decode("ascii")
            sum_time1 += float(out.split("\n")[0])
            #print(out.split("\n")[1], end=" ")
        if cb and minmod in (False, "BOTH"):
            out = subprocess.check_output(["python3.7", "cb_witness.py", "-orig", TEMP_THEORY, TEMP_MODEL]).decode("ascii")
            #print(out)
            assert(out.split("\n")[1] == "NO")
            

            sum_time1 += float(out.split("\n")[0])
            #out = subprocess.check_output(["python3.7", "cb_witness.py", "-v2", TEMP_THEORY, TEMP_MODEL]).decode("ascii")
            #sum_time2 += float(out.split("\n")[0])
        if not cb and minmod in (False, "BOTH"):
            out = subprocess.check_output(["python3.7", "check_min.py", TEMP_THEORY, TEMP_MODEL]).decode("ascii")      
            sum_time2 += float(out.split("\n")[0])
        
        '''if k <= 40:
            out = subprocess.check_output(["python3.7", "is_min_model.py", TEMP_THEORY, TEMP_MODEL]).decode("ascii")
            sum_time3 += float(out.split("\n")[0])'''
        t-=1
       
    latex.append((k, sum_time1/tinitial, sum_time2/tinitial))
    if sum_modlen > 0:
        print("modlen: ", sum_modlen/tinitial)
    if sum_minmodlen > 0:
        print("minmodlen: ", sum_minmodlen/tinitial)
    print(k, sum_time1/tinitial, sum_time2/tinitial)

def testsatcomp(file):
    with open(file, "r") as f:
        content = f.read()
    with open(TEMP_THEORY, "w") as f:
        f.write(content)

    try:
        # weird exit status
        subprocess.check_output(["minisat", TEMP_THEORY, TEMP_MODEL])
    except:
        pass
    with open(TEMP_MODEL, 'r') as f:
        model = f.read().replace('\n', '')
    model = model.replace("SAT", "")
    model = [int(x) for x in model.split() if int(x) > 0]
    with open(TEMP_MODEL, 'w') as f:
        f.write(' '.join(str(atom) for atom in model))
    print(len(model))
    try:
        out = subprocess.check_output(["python3.7", "check_min.py", TEMP_THEORY, TEMP_MODEL], timeout=120).decode("ascii")     
    except Exception as e:
        print(e)
        return
    print(out)

def test_directory(_cdir='/public/home/wys/witness/v3/data/', # test all the files in the given directory, minimal model / answer set is given
                  mus=True, save=True, mh=False, is_LP=False, q=True): 
    if is_LP:  
        _pos_ins, _pos_mod = ".lp", ".m"
    else:
        _pos_ins, _pos_mod = ".cnf", ".m-m"

    instances = glob.glob(_cdir+"/*"+_pos_ins) ## get all the directory under the given directory, e.g., 3CNF/50, 3CNF/60, ..., sat/Callatz, ..., handcrafted
    model = [x.replace(_pos_ins, _pos_mod) for x in instances]
    if save:
        wits = [x.replace(_pos_ins, ".wit") for x in instances]
        if mh: wits = [x +"-mh" for x in wits]
        if mus: wits = [x + "-mus" for x in wits]
 
    __command = ["python3.7", "cb_witness.py", "-v4", "-q", "-check_compact", "-TT_PYSAT"]
    if is_LP: __command.append("-lp")
    if mus: __command.append("-MUS_Solver=picomus")
    if mh  : __command.append("-mh")
    for i in range(len(instances)):
        if not os.path.exists(model[i]): continue
        with open(model[i],"r") as _f:
           __li = _f.readline()
           if len(__li) == 0 or \
              __li.find("UNSAT") >= 0 or \
              __li.find("out_of_time") >= 0 or \
              __li.find("UNKNOWN") >= 0: continue
        try:
           _command = __command + [instances[i], model[i]]
           out = subprocess.check_output(_command, text=True, timeout=time_out)
        except subprocess.CalledProcessError as e:
           out = e.output
           continue
        except RecursionError as e: 
           out = "recursion error"
 
        except subprocess.TimeoutExpired as e:
           out = "time out"

        if save: # also save witness
           with open(wits[i],"w") as f: f.write(out)


def test_mbw_kCNF(_cdir='/public/home/wys/witness/v3/data/', lower=50, upper=200, clen=3, 
                  MIN_MODEL=0, MIN_CHECK=False,
                  mus=True, save=True, mh=True):  ### test the random k-CNFs at given directory
    step = 0.1
    y=3.0
    while (y <= 5.0):
        steps.append(y)
        y = round(y + 0.1,1)
    _pdir = ""
    if save:
        _pdir = _cdir + str(clen) + 'CNF/' #+str(k)
        if not os.path.exists(_pdir):
            os.system('mkdir '+_pdir)
    #os.system("echo k ration time sat_dlv_out wt_out len_2 >" + OUT_PUT)
    for k in range(lower,upper+1,10): ### yisong
        if save:  # for clen-CNF/atoms/
            _pdir = _cdir + str(clen) + "CNF/" + str(k)
            if not os.path.exists(_pdir): os.system('mkdir '+_pdir)

        for c in steps:
            test_v4(CLAUSES = int(c*k), ###  5*k, due to the phase transition of 3-SAT whose cirtical point is about 4.2
                ATOMS=k,
                CLAUSE_LENGTH=clen, #3,
                HEAD_PROPORTION="UNIFORM",
                #cb=True,
                #minmod=True,
                #k=k,
                #useminmodels=False,
                fixclauselen=True,
                bMUS=mus,
                MIN_MODEL=MIN_MODEL,
                MIN_CHECK = MIN_CHECK,
                save_model=save,
                mh = mh,
                _pdir = _pdir)

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Run test')
    parser.add_argument("-lower", type=int, default=1, help = "The lower bound of number of atoms")
    parser.add_argument("-upper", type=int, default=1, help = "The upper bound of number of atoms")
    parser.add_argument("-clen", type=int, default=3, help = "The length of every clauses")
    parser.add_argument("-mus", action='store_true', help = "Use MUS solver picomus")
    parser.add_argument("-ms", type=int, default=0, help = "The solver for computing minimal model, 0: cadical, 1: clingo, 2: dlv")
    parser.add_argument("-mc", action='store_true', help = "Whether do minimal model checking")
    parser.add_argument("-mm", action='store_true', help = "Just compute minimal model by for solvers")
    parser.add_argument("-save", action='store_true', help = "Save the minimal model, cnf and witness")
    parser.add_argument("-dir", type=str, default="", help = "The path to compute minimal beta witness")
    parser.add_argument("-lp", action='store_true', help = "The -dir is for logic programs")
    parser.add_argument("-mh", action='store_true', help = "Print the multiple witnesses")
    parser.add_argument("-q", action='store_true', help = "silient")
   
    args = parser.parse_args()

    k = 2   
    CLAUSES = 50
    ATOMS = 2*math.sqrt(2*k)
    CLAUSE_LENGTH = math.sqrt(2*k)
    HEAD_PROPORTION = 0.8

    t = 10
    time_out = 1800
    TEMP_THEORY += str(os.getpid())
    TEMP_MODEL  += str(os.getpid())
    TEMP_MIN_MODEL += str(os.getpid())
    TEMP_DLV += str(os.getpid())
    TEMP_CLASP += str(os.getpid())
    SAT_INPUT += str(os.getpid())
  
    if args.mm:
        test_v5(args.lower)
        sys.exit(0)

    #testsatcomp("test_data/testcases/satcomp/planning/logistics.a.cnf")
    '''for i in range(7, 10):
        print(str(i) + "," + str(cbwitness_worstcase(i)))'''
    lower = args.lower 
    upper = args.upper
    MIN_MODEL = 0
    MIN_CHECK = False
   
    OUT_PUT = OUT_PUT +  str(args.lower)  + "_" + str(args.upper) +"_"
    
    MIN_MODEL = args.ms #int(sys.argv[3]) # determine which minimal model solver is used
    OUT_PUT_MIN = OUT_PUT_MIN + str(lower) +"_" + str(upper) + "_" + str(os.getpid())
    MIN_CHECK = args.mc #True # whether do minimal check
    
    '''
    if len(sys.argv) >= 3:
        # usage [<lower> <upper>] 
        lower = int(sys.argv[1])
        upper = int(sys.argv[2])
        OUT_PUT = OUT_PUT +  sys.argv[1] + "_" + sys.argv[2] +"_"
        if len(sys.argv) >= 4:
            MIN_MODEL = int(sys.argv[3]) # determine which minimal model solver is used
        if len(sys.argv) == 5 and sys.argv[4] == "mc":
            OUT_PUT_MIN = OUT_PUT_MIN + str(lower) +"_"+str(upper) + "_"+ str(os.getpid())
            MIN_CHECK = True # whether do minimal check
    OUT_PUT += str(os.getpid())
    step = 0.1 
    y=3.0    
    while (y <= 5.0):
        steps.append(y)
        y = round(y + 0.1,1) 
    _cdir =   '/public/home/wys/witness/v3/data/'
    _pdir = ""
    if args.save:
        _pdir = _cdir + str(args.clen) + 'CNF/' #+str(k)
        if not os.path.exists(_pdir): 
            #os.system('rm -fr '+ _pdir)
        #else: 
            os.system('mkdir '+_pdir)
    os.system("echo k ration time sat_dlv_out wt_out len_2 >" + OUT_PUT)
    for k in range(lower,upper+1,10): ### yisong
        if args.save:  # for clen-CNF/atoms/
            _pdir = _cdir + str(args.clen) + "CNF/" + str(k)
            if not os.path.exists(_pdir): os.system('mkdir '+_pdir)

        for c in steps:
            test_v4(CLAUSES = int(c*k), ###  5*k, due to the phase transition of 3-SAT whose cirtical point is about 4.2
                ATOMS=k, 
                CLAUSE_LENGTH=args.clen, #3, 
                HEAD_PROPORTION="UNIFORM", 
                #cb=True, 
                #minmod=True, 
                #k=k, 
                #useminmodels=False,
                fixclauselen=True,
                bMUS=args.mus,
                MIN_MODEL=MIN_MODEL, 
                MIN_CHECK = MIN_CHECK,
                save_model=args.save,
                _pdir = _pdir)
    for i in range(2, 21):
        print(str(i) + "," + str(checkMin_worstcase(i)))'''
    '''
    for (k,t1,t2,out_times) in latex: ### Yisong 
        if t1 == 0:
            print("{0}, {1:.6f}, {2}".format(k, t2, out_times))
        elif t2 == 0:
            print("{0}, {1:.6f}, {2}".format(k, t1, out_times))
        else:
            print("{0}, {1:.6f}, {2:.6f}, {3}".format(k, t1, t2, out_times))
    '''
    if args.dir == "":
        test_mbw_kCNF(_cdir='/public/home/wys/witness/v3/data/', lower=args.lower, upper=args.upper, clen=args.clen,
                      MIN_MODEL=args.ms, MIN_CHECK=args.mc,
                      mus=args.mus, save=args.save, mh=args.mh)
    else:
        test_directory(_cdir=args.dir, mus=args.mus, save=args.save, mh=args.mh, is_LP=args.lp, q=args.q)
    try:
        if not args.save:
            os.remove(TEMP_THEORY)
            os.remove(TEMP_MIN_MODEL)
        os.remove(TEMP_DLV)
        os.remove(TEMP_MODEL)
        os.remove(SAT_INPUT)
        os.remove(TEMP_CLASP)
        #os.remove(OUT_PUT)
    except:
        pass 
