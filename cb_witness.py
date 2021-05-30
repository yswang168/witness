from lib.logic_program import Rule, DisLP
from lib.parser import cnf_parser, model_parser
from lib.atom_set import AtomSet
from lib.clause_theory import ClauseTheory
from lib.super_dependency_graph import generate_super_dependency_graph_from_theory
from lib.logic import minimal_witness, closure_under, minimal_witnesses, minimal_witness_new, get_MUS, get_new_derived
import lib.logic
import sys
import time
import argparse
import resource, signal, copy

sys.setrecursionlimit(10000)
# using MUS solver
MUS_Solver = None

### Added by Yisong
def main_v4(Sigma: 'ClauseTheory', M: 'AtomSet'):
    # M: a minimal model of Sigma
    B = list() # to keep the compact beta witness
    #####Sig = Sigma.minimal_reduct(M)  # MR reduct ##### THIS HAS BEEN IMPLIMENTED IN THE MAIN FUNCTION
    Sig = Sigma
    SG =  generate_super_dependency_graph_from_theory(Sig)
    ## b_SG  = copy.deepcopy(SG) ## keep it for computing the previous dependency nodes, a simple way is to use all 
    DS=AtomSet()  # the established atoms
    SG.remove_empty_sources() ## remove all empty sources
    sources = SG.get_sources()
    while len(sources) > 0:
        S = list(sources)[0]
        SA = S.get_atoms()
        B.extend(main_algorithm_v4(Sig, SA, DS))
        DS = DS.union(SA)
        SG.remove_node(S)
        SG.remove_empty_sources()
        sources = SG.get_sources()
    return B
 
def main_algorithm_v4(Sigma: 'ClauseTheory', M: 'AtomSet', S: 'AtomSet'):
    T = S
    Sigma.reduce_cb(T)
    res = []
    while len(M.difference(T)) != 0:
        ## unit propagation
        while(True): 
            Sigu = ClauseTheory()
            for clause in Sigma:
                if clause.len_positive() == 1 and \
                    clause.get_negative().get_atoms().issubset(T.get_atoms()) and \
                    not clause.get_positive().get_atoms().issubset(T.get_atoms()): 
                        Sigu.add_clause(clause)
                        u = list(clause.get_positive().get_atoms())[0]
                        res.append((u, Sigu))
                        Sigma.remove_clause(clause)
                        T.add(u)
                        break
            if Sigu.len() == 0: break 

        MT = M.difference(T)
        if MT.is_empty(): break
        u = list(MT)[0]
        Sigu = get_MUS(Sigma, AtomSet([u]), T, MUS_Solver) ## assert Sigu is not empty
        v = get_new_derived(Sigu, AtomSet([u]), T)
        while (v != None):
            u = v
            Sigu = get_MUS(Sigu, AtomSet([u]), T, MUS_Solver)
            v = get_new_derived(Sigu, AtomSet([u]), T)
        res.append((u,Sigu))
        T.add(u)

        ## The following cannot be true, there is a counterexample
        ''' 
        -1 2 0
        -2 3 0
        -3 1 0
        1 2 0
        with minimal model {1,2,3}
        '''
        #for clause in Sigu:
        #    Sigma.remove_clause(clause)

    return res
###

def main_algorithm_v3(Sigma: 'ClauseTheory', M: 'AtomSet', S: 'AtomSet'):
    T = S
    Sigma.reduce_cb(T)
    res = []
    while len(M.difference(T)) != 0:
        Sigma_v = ClauseTheory()
        for alpha in Sigma:
            Sigma_v.add_clause(alpha)
            follows = closure_under(Sigma_v, T, Sigma_v.get_all_atom_nums().intersection(M.difference(T)))
            if len(follows)>0:
                break
        else:
            return None
        check = follows
        for alpha in ClauseTheory(Sigma_v.get_clauses()):
            Sigma_v.remove_clause(alpha)
            follows = closure_under(Sigma_v,T,check)
            if len(follows) > 0:
                check = check.intersection(follows)
            else:
                Sigma_v.add_clause(alpha)
        v = check.pop()
        res.append((v, Sigma_v))
        T.add(v)
        Sigma.reduce_cb(T)
    return res


def main_algorithm_v2(Sigma: 'ClauseTheory', M: 'AtomSet', S: 'AtomSet'):
    T = S
    Sigma.reduce_cb(T)
    res = []
    while len(M.difference(T)) != 0:
        breakall = False
        # build subsets of Sigma with increasing size
        for i in range(1, len(Sigma)+1):
            for Sigma_prime in Sigma.combinations(i):
                symbols = Sigma_prime.get_all_atom_nums().difference(T)
                # check if this subset is a minimal witness for any of the atoms in M-T
                for p in M.difference(T):
                    if lib.logic.TT[lib.logic.TT_sel](Sigma_prime, AtomSet([p]), symbols, T):
                        # Sigma_prime is a minimal witness for p and Sigma_prime has no witness contribution to any other atom in M-T
                        T.add(p)
                        Sigma.reduce_cb(T)
                        res.append((p, Sigma_prime))
                        breakall = True
                        break
                if breakall:
                    break
            if breakall:
                break
        if not breakall:
            return None
    return res

def main_algorithm_subroutine(Sigma_u, Delta_u, T, res):
    for i in range(1, len(Sigma_u)+1):
        for Sigma_v in Sigma_u.combinations(i):
            symbols = Sigma_v.get_all_atom_nums().difference(T)
            for v in Delta_u:
                if lib.logic.TT[lib.logic.TT_sel](Sigma_v, AtomSet([v]),symbols, T):
                    res.append((v, Sigma_v))
                    T.add(v)
                    Delta_u.remove(v)
                    return

def main_algorithm_subroutine_new(Sigma_u, Delta_u, T, res):
    Sigma_v = ClauseTheory(Sigma_u.get_clauses())
    check = Sigma_u.get_all_atom_nums().intersection(Delta_u)
    
    for clause in Sigma_u:
        Sigma_v.remove_clause(clause)
        follows = closure_under(Sigma_v, T, check)
        if len(follows) > 0:
            check = check.intersection(follows)
        else:
            Sigma_v.add_clause(clause)
    v = check.pop()
    res.append((v, Sigma_v))
    Delta_u.remove(v)
    T.add(v)



def main_algorithm(Sigma: 'ClauseTheory', M: 'AtomSet', S: 'AtomSet', wit_old: bool):
    T = S
    Sigma.reduce_cb(T)
    res = []
    # O(|M|+|T|) for loop check
    while len(M.difference(T)) != 0:
        # get random element O(|M|+|T|)
        u = next(iter(M.difference(T)))
        # O(2^|Sigma|*2^|A|)
        if wit_old:
            Sigma_u = minimal_witness(Sigma, u, T)
        else:
            Sigma_u = minimal_witness_new(Sigma, u, T)
        if Sigma_u == None:
            return None
        #print(Sigma_u)
        # O(|A|*2^|Sigma|)
        # We do not need to check for T and u surely follows
        Delta_u = closure_under(Sigma_u, T, Sigma_u.get_all_atom_nums().difference(T).difference(AtomSet([u])))
        # u surely follows
        Delta_u.add(u)

        # we know Sigma_u has no witness contribution to other atoms
        if len(Delta_u) == 1:
            res.append((u, Sigma_u))
            T.add(u)
            continue
        
        while len(Delta_u) != 0:
            # check for other witness contribution from Sigma_u
            # O(|Delta_u|*2^|Sigma_u|*|A(Sigma_u)-T|^2)

            # Implementation 1
            if wit_old:
                main_algorithm_subroutine(Sigma_u, Delta_u, T, res)
            else:
                main_algorithm_subroutine_new(Sigma_u, Delta_u, T, res)
            Sigma_u.reduce_cb(T)
        Sigma.reduce_cb(T)
            
    return res

def OutOfTime(signum, frame):
    print("Out of time.")
#    sys.exit(0)

def is_compact(res): # res is a minimal beta-witness, which is a list of pairs (atom, witness)
    for i in range(len(res)):
       if len(res[i][1]) == 1: continue
       
       for j in range(len(res)):
           if j==i: continue
           
       #for j in range(i+1, len(res)):
       #    if len(res[j][1]) == 1: continue
           # checking for each clause c in res[i][1], whether it is occurs in the witness res[j][1]
           for c1 in res[i][1]:
               for c2 in res[j][1]:
                  if c1 == c2: return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run cbwitness')
    parser.add_argument("file_CNF", help = "theory file")
    parser.add_argument("file_M", help = "model file")
    parser.add_argument("-file_S", type = str, help = "S file", required=False) # part of atoms in M
    parser.add_argument("-MUS_Solver", type = str, help = "MUS solver", required=False)  
    grouptt = parser.add_mutually_exclusive_group(required = True)
    grouptt.add_argument("-TT_OLD", help="use enumeration algorithm for consequence checking",action = "store_true")
    grouptt.add_argument("-TT_SAT", help="use sat solver for consequence checking (large overhead for file generation", action = "store_true")
    grouptt.add_argument("-TT_PYSAT", help="use pysat package with glucose4 for consequence checking", action = "store_true")
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-orig", action = "store_true", help="use the original algorithm proposed in the original paper")
    group.add_argument("-v2", action = "store_true", help="use the second version of the algorithm suited for small minimal witnesses")
    group.add_argument("-v3", action = "store_true", help="use the third version of the algorithm just mentioned in the thesis. It first adds clauses to Sigma_v until atoms follow and then removes them until just one atom is the consequence (pair (v,Sigma_v))")
    group.add_argument("-v4", action = "store_true", help="use unit propagation at first in each iteration")
    parser.add_argument("-WITNESS_OLD", help = "unoptimized version of the algorithm (enumerating over all theory subsets and no theory reducing)\n"+
        "Just possible with the original version (-orig argument)", action='store_true')
    parser.add_argument("-REDUCE", help = "reduce theory every time an atom is added to the set T", action='store_true')
    parser.add_argument("-lp", help="The theory file is a logic program", action='store_true',default=False)
    #parser.add_argument("-lparse", help="The logic program is in lparse format", action='store_true',default=False)
    parser.add_argument("-q", help="be quiet", action='store_true',default=False)
        
    ## Added by XXXX for time out
    parser.add_argument("-t", action="store", type=int, dest="mct", help="CPU limit (s)", default=-1)
    ##
    ## Added by yisong Wang for print the clauses with multi heads after minimal reduct in witness
    parser.add_argument("-mh", action="store_true", help="print the rules with multi head atoms after minimal reduct in witness")
    parser.add_argument("-check_compact", action="store_true", help="Checking if the witness is compact")

    args = parser.parse_args()
    if (args.WITNESS_OLD and 
        args.orig not in vars(args)):

        parser.error('The -WITNESS_OLD argument requires the -v2 argument')
    #print(args)

    ## set the signal handler for out of time
    ## signal.signal(signal.SIGXCPU, OutOfTime)
    ##
    dlp = DisLP()
    clause_theory_b = ClauseTheory()
    gr_ids = None ### to record the indexs
    resource.setrlimit(resource.RLIMIT_CPU, (args.mct, args.mct))
    signal.signal(signal.SIGXCPU, OutOfTime)
    ##
    try:
        orig = args.orig == True
        v2 = args.v2 == True
        v3 = args.v3 == True
        v4 = args.v4 == True
        lp = args.lp == True
        if args.MUS_Solver != None: MUS_Solver = args.MUS_Solver
        if not args.REDUCE:
            # TODO: ugly way of solving this
            ClauseTheory.reduce_cb = lambda x,y: None
        if args.TT_OLD:
            lib.logic.TT_sel = "TT_OLD"
        elif args.TT_SAT:
            lib.logic.TT_sel = "TT_SAT"
        elif args.TT_PYSAT:
            lib.logic.TT_sel = "TT_PYSAT"

        if not lp:
            M = model_parser(args.file_M)
            if len(M) == 0: # unknown model or empty model
                print("Unknown or empty model")
                exit(0)
            if args.file_S != None:
                S = model_parser(args.file_S)
            else:
                S = AtomSet()
            clause_theory_b = cnf_parser(args.file_CNF)  ## changed by Yisong for keep use later 
        else:
            dlp.build_DLP(args.file_CNF)
            M = model_parser(args.file_M, dlp)
            if args.file_S != None:
                S = model_parser(args.file_S, dlp)
            else:
                S = AtomSet()
            v_dlp, gr_ids = dlp.GL_reduct(M)
            clause_theory_b = v_dlp.To_ClauseTheory()
        
        all_atom_nums = clause_theory_b.get_all_atom_nums()
        for atom in M:
            if not atom in all_atom_nums:
                print("model uses an atom which does not exist in given theory")
                exit(1)
        for atom in S:
            if not atom in all_atom_nums:
                print("S uses an atom which does not exist in given theory")
                exit(1)
    #clause_theory.reduce(AtomSet(), AtomSet({2}))
    #clause_theory.reduce(AtomSet({1}), AtomSet())
    #clause_theory.reduce(AtomSet(), AtomSet({5, 6}))
    #model = AtomSet({4})
#    try:
        #_clause_theory_b = ClauseTheory(clause_theory_b)
        clause_theory, _mr_ids = clause_theory_b.minimal_reduct(M.union(S), _ids= gr_ids)
        _clause_theory = ClauseTheory(clause_theory)
        #start = time.time()
        if orig:
            res = main_algorithm(clause_theory, M, S, args.WITNESS_OLD)
        elif v2:
            res = main_algorithm_v2(clause_theory, M, S)
        elif v3:
            res = main_algorithm_v3(clause_theory, M, S)
        elif v4:
            res = main_v4(clause_theory, M)

        #end = time.time()
        #print(end-start)
        bCompact = None
        if res == None:
            print("NO")
        else:
            print("YES")
            if not args.q:
                if not lp :
                    print(sorted(M.get_atoms())) ### Yisong
                else:
                    print(sorted([dlp.get_to_atom_set()[x] for x in M]))
            head_2, clause_head_2, n_clause_2 = 0, 0, 0 ### the number of claues in witness whose head has size >= 2
            ###

            for atom, witness in res:
                ### print("{0} from {1}".format(atom, witness))    ### Yisong      
                if len(witness) > 1:
                    n_clause_2 += len(witness)
                    head_2 += 1
                    if args.mh and args.q: 
                        _cs, __ids = _clause_theory.find_MR_clauses(witness, M, _mr_ids, with_M=False)
                        if not lp:
                            print("{0}:\n {1}".format(atom, clause_theory_b.from_indices(__ids)))
                        else:
                            print("{0}:".format(dlp.get_to_atom_set()[atom]))
                            dlp.print_indices(__ids)                  
                for cl in witness:
                    if cl.len_positive() > 1: 
                        clause_head_2 += 1
                        ## start 2021.5.5
                        ## print these rules/clauses according the paramenter -mt
                        #h2_clauses.append(cl)
                        #if args.mh and args.q: 
                        ### just print the witness
                        #   print("{0}:{1}".format(atom, witness))
                        '''
                           if lp: 
                                print(dlp.get_to_atom_set()[atom] + ":")
                                dlp.find_GL_MR_rules(witness,M).print() 
                           else:
                                print("{0}:\n {1}".format(atom, clause_theory_b.find_MR_clauses(witness, M)))
                        '''
                        #### end 2021.5.5

                
                if not args.q:
                    _cs, __ids = _clause_theory.find_MR_clauses(witness, M, _mr_ids, with_M=False)
                    if not lp:
                        print("{0}:\n {1}".format(atom, clause_theory_b.from_indices(__ids)))
                    else:
                        #print("{0}:\n {1}".format(atom, dlp.from_indices(__ids)))
                        print("{0}:".format(dlp.get_to_atom_set()[atom]))
                        dlp.print_indices(__ids)                  
                
            print("{0} {1} {2} atoms, head>2 clauses, clauses".format(head_2, clause_head_2, n_clause_2 ))
            #print("%d clauses have head size >=2"%head_2, end='')
            #print(" {0} {2}".format(clause_head_2, n_clause_2))
            ### checking if it is compact
            if head_2 >= 1 and args.check_compact:
                bCompact = is_compact(res)
        # modified by XXXX wang
        # 2019.11.13
        # compute the CPU time by resource.getrusage
        rusage=resource.getrusage(resource.RUSAGE_SELF)
        print("Time: %.3f (s)"%(rusage.ru_utime+rusage.ru_stime))
        print("Memory: %.3f (M)"%(rusage.ru_maxrss/1024))
        print("The witness is compact: ",end='')
        if args.check_compact and bCompact == None:
           bCompact = True 
        print(bCompact)
    except ValueError as e:
        print(e)
    except MemoryError as e:
        print("Out of memory")
    except RecursionError as e:
        print("Our of recursion limitation")
    except TimeoutExpired as e: #TimeoutError as e:
        print("Out of time.")
    except: 
        print("error.")
