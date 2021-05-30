from .clause_theory import ClauseTheory
from .atom_set import AtomSet
from collections import deque
from .graph import AtomNode
import subprocess
import os
import random 
from pysat.solvers import Glucose4
from pysat.formula import CNF

# checks if an atomset is a minimal model of a theory using the theorem from paper2
# so it checks if the atomset is the deductive closure of the minimal reduct of the theory under the atomset
def is_minimal_model(theory: 'ClauseTheory', atom_set: 'AtomSet'):
    minimal_reduct = theory.minimal_reduct(atom_set)
    symbols = minimal_reduct.get_all_atom_nums().union(atom_set)
    if atom_set != minimal_reduct.get_all_atom_nums():
        return False
    #print(atom_set, symbols)
    #print(TT_check_all_and(minimal_reduct, atom_set, symbols, AtomSet()))
    #print(not TT_check_all_or(minimal_reduct, symbols.difference(atom_set), symbols, AtomSet()))
    # check if all atoms of the atomset are implied and none others
    return (TT[TT_sel](minimal_reduct, atom_set, symbols, AtomSet()))

# check if a knowledgebase implies all of a set of atoms a, using all combinations of symbols
# start with the empty model
def TT_check_all_old(KB: 'ClauseTheory', a: 'AtomSet', symbols: 'AtomSet', model: 'AtomSet'):
    #print(KB, a, symbols, model)
    if len(symbols) == 0:        
        if KB.pl_true(model):
            return len(a.difference(model)) == 0
        else:
            return True
    P = symbols.pop()
    model.add(P)
    ret = TT_check_all_old(KB, a, symbols, model)
    model.remove(P)
    ret = ret and TT_check_all_old(KB, a, symbols, model)
    symbols.add(P)
    return ret

def TT_check_all(KB: 'ClauseTheory', a: 'AtomSet', symbols: 'AtomSet', model: 'AtomSet'):
    strings = []
    num_atoms = len(KB.get_all_atom_nums().union(a))
    strings.append("p cnf {0} {1}".format(num_atoms, len(KB)+1+len(model)))
    strings.append("\n")
    for clause in KB:
        for atom in clause.get_positive():
            strings.append(str(atom))
            strings.append(" ")
        for atom in clause.get_negative():
            strings.append(str(-atom))
            strings.append(" ")
        strings.append("0\n")
    for atom in model:
        strings.append(str(atom))
        strings.append(str(" 0\n"))
    for atom in a:
        strings.append(str(-atom))
        strings.append(" ")
    strings.append("0\n")
    with open('satttentails', 'w') as f:
            f.write(''.join(strings))
    try:
        # weird exit status
        subprocess.check_output(["minisat", "satttentails", "modelttentails"], stderr = subprocess.DEVNULL)
    except:
        pass
    with open('modelttentails', 'r') as f:
        model = f.read()
    if "UNSAT" in model:
        return True
    return False

def TT_check_all_pysat(KB: 'ClauseTheory', a: 'AtomSet', symbols: 'AtomSet', model: 'AtomSet'):
    formula = CNF()
    for clause in KB:
        arr = []
        arr.extend(clause.get_positive().get_atoms())
        arr.extend(map(lambda x: -x, clause.get_negative().get_atoms()))
        formula.append(arr)
    assumptions = []
    assumptions.extend(model)
    formula.append(list(map(lambda x: -x, a)))
    with Glucose4(bootstrap_with=formula.clauses) as g:
        return not g.solve(assumptions = assumptions)

    
TT_sel = "TT_OLD"
TT = {}
TT["TT_OLD"] = TT_check_all_old
TT["TT_SAT"] = TT_check_all
TT["TT_PYSAT"] = TT_check_all_pysat   
    
'''# see TT_check_all_and but checks if the knowledgebase implies any of the atoms in a
def TT_check_all_or(KB: 'ClauseTheory', a: 'AtomSet', symbols: 'AtomSet', model: 'AtomSet'):
    #print(KB, a, symbols, model, len(symbols))
    if len(symbols) == 0:
        if KB.pl_true(model):
            return len(a.intersection(model)) != 0
        else:
            return True
    P = symbols.pop()
    model.add(P)
    ret = TT_check_all_or(KB, a, symbols, model)
    model.remove(P)
    ret = ret and TT_check_all_or(KB, a, symbols, model)
    symbols.add(P)
    return ret

# Checks if the knowledgebase KB implies a
def TT_check_all(KB: 'ClauseTheory', a: int, symbols: 'AtomSet', model: 'AtomSet'):
    if len(symbols) == 0:
        if KB.pl_true(model):
            return a in model
        else:
            return True
    P = symbols.pop()
    model.add(P)
    ret = TT_check_all(KB, a, symbols, model)
    model.remove(P)
    ret = ret and TT_check_all(KB, a, symbols, model)
    symbols.add(P)
    return ret'''

#old version
# Calculates a minimal witness for u under the theory Sigma and the set of atoms T
# O(2^|Sigma|*2^|A|) where A are all the atoms in Sigma
def minimal_witness(Sigma, u, T):
    #Check all subsets with increasing size
    for i in range(1, len(Sigma) + 1):
        for Sigma_c in Sigma.combinations(i):
            symbols = Sigma_c.get_all_atom_nums().difference(T)            
            symbols.add(u)
            if TT[TT_sel](Sigma_c, AtomSet([u]), symbols, T):
                # Sigma_c implies u and is a minimal witness because no subset implied u
                return Sigma_c
    return None
# Calculates a minimal witness for u under the theory Sigma and the set of atoms T
def minimal_witness_new(Sigma, u, T):
    if not TT[TT_sel](Sigma, AtomSet([u]), Sigma.get_all_atom_nums().difference(T), T):
        return None

    Sigmaret = ClauseTheory(Sigma.get_clauses())

    for clause in Sigma:
        Sigmaret.remove_clause(clause)
        if not TT[TT_sel](Sigmaret, AtomSet([u]), Sigmaret.get_all_atom_nums().difference(T), T):
            Sigmaret.add_clause(clause)
    return Sigmaret

# returns all minimal witnesses for v under the theory Sigma and the set of atoms T
# O(2^|Sigma|*2^|A|) where A are all the atoms in Sigma
# space complexity is pretty big, keeps increasing sizes of subsets in memory, O((|Sigma| over |Sigma|/2)*|Sigma|)
def minimal_witnesses(Sigma, v, T):
    #TODO better implementation, note that this function is not used
    min_witnesses = list()
    combs = deque()
    combs.append((0, list()))
    #Check all subsets with increasing size using a queue
    while len(combs) > 0:
        startidx, indices = combs.popleft()
        Sigma_v = Sigma.from_indices(indices)
        # other option?
        if any(len(Sigma_v.difference(min_witness)) == 0 for min_witness in min_witnesses):
            continue
        symbols = Sigma_v.get_all_atom_nums().union(T)
        symbols.add(v)
        if TT[TT_sel](Sigma_v, v, symbols, T):
            # Do not check bigger subsets
            yield Sigma_v
            #min_witnesses.append(Sigma_v)
        else:
            # check for bigger subsets, namely size+1
            for i in range(startidx, len(Sigma)):
                indices_plus = list(indices)
                indices_plus.append(i)
                combs.append((i+1, indices_plus))

# calculates the closure under a theory Sigma under a set of atoms T
# just checks for atoms A, if these are implied by the theory
# O(|A|*2^|B|) where B are all the atoms in Sigma
def closure_under(Sigma, T, A):
    symbols = Sigma.get_all_atom_nums().union(A).difference(T)
    
    ret = AtomSet()
    for atom in A:
        if TT[TT_sel](Sigma, AtomSet([atom]), symbols, T):
            ret.add(atom)
    return ret

# checks if a given Theory has the one-source-head property from paper1
# SG is the superdependency-graph for this theory
# SG is not allowed to have empty sources
def has_OSH_property(T: 'ClauseTheory', SG: 'SuperDependencyGraph') -> bool:
    for setnode in SG.get_sources():
        atoms = [node.get_val() for node in setnode.get_subnodes() if isinstance(node, AtomNode)]
        check = True
        for atom in atoms:
            for clause in T.get_clauses():
                if (atom in clause.get_positive()) and not all((atomprime in atoms) for atomprime in clause.get_positive()):
                    check = False
                    break
        if check:
            return True
    return False

### Yisong
def get_MUS(Sigma: 'ClauseTheory', T: 'AtomSet', A: 'AtomSet', MUS_solver = None) -> ClauseTheory :
#   get a minimal subset S of Sigma such that S \cup A \models T
    if MUS_solver != None:
        return get_MUS_S(Sigma, T, A, MUS_solver)
    
    symbols = Sigma.get_all_atom_nums().union(A).difference(T)
    S = ClauseTheory(Sigma.get_clauses())
    Checked = ClauseTheory()
    for clause in Sigma: 
        if clause in Checked: continue
        S.remove_clause(clause)
        if TT[TT_sel](S, T,  symbols, A): continue
        else:
            S.add_clause(clause)
            Checked.add_clause(clause)        
    return S

### Yisong
#   get a minimal subset S of Sigma such that S \cup A \models T
#   by calling an MUS solver
#   picomus as default
def get_MUS_S(Sigma: 'ClauseTheory', T: 'AtomSet', A: 'AtomSet', Solver='picomus') -> ClauseTheory :
    # get the max ID of atom
    maxID = 0
    for cl in Sigma:
        maxID = max(maxID, max(cl.get_atoms()))
    maxID = max(maxID, max(T.get_atoms())) 
    if len(A) > 0:
        maxID = max(maxID, max(A.get_atoms()))                
    nclause = len(Sigma) + len(T) + len(A)
    # build the CNF file 
    fn = "/tmp/"+ str(os.getpid()) + "_" + str(random.randint(100,999)) + ".cnf"
    fp = open(fn, "wt")
    
    print("p cnf %d %d"%(maxID, nclause), file=fp)
    for atom in A:
        print("%d 0" % atom, file = fp)
    #for atom in T:
    #    print("-%d 0"%atom, file=fp)
    for atom in T:
        print("-%d"%atom, file=fp, end=" ")
    print("0", file=fp)
       
    ClauseList = list() 
    for clause  in Sigma:
        ClauseList.append(clause)
        cls = " ".join(map(str, clause.get_positive().get_atoms())) + " " + " ".join(map(str, map(lambda x:-x, clause.get_negative().get_atoms()))) + " 0\n"
        fp.write(cls)
    fp.close()
    
    # call the MUS solver
    tmp_f = fn.replace(".cnf", ".mus")
    ft = open(tmp_f,"wt")
    output= subprocess.call([Solver, fn],stdout=ft)
    ft.close()
    ft = open(tmp_f,"rt")
    line = ft.readlines()
    ft.close()
    # resolve the output of the solver's output
    m_sig = ClauseTheory()
    lenA = len(A)
    lenT = len(T) 
    PreLen = lenA+lenT
    #lines = output.split("\n")
    for i in range(len(line)):
        if line[i][0] == 'c': continue
        if line[i][0] == 's': 
            assert(line[i].find("UNSAT") != -1)
            continue
        if line[i][0] == 'v':
            intc = int(line[i].split(" ")[1])
            if intc == 0 or intc <= PreLen: # end of the MUS file of the first len(T)+lenA lines is the  
                continue
            m_sig.add_clause(ClauseList[intc - PreLen -1])
    # remove the temp files
    os.remove(tmp_f)
    os.remove(fn)
    return m_sig
    

def get_new_derived(Sigma: 'ClauseTheory', T: 'AtomSet', A: 'AtomSet'):
# get a new atom different from the ones in T and A that is derived from Sigma and A
# return this atom if found
# None otherwise
    symbols = Sigma.get_all_atom_nums()
    Mt = Sigma.get_all_atom_nums().difference(T.union(A))
    for atom in Mt:
        if TT[TT_sel](Sigma, AtomSet([atom]), symbols, A): return atom
    return None
    
