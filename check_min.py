from lib.parser import cnf_parser, model_parser
from lib.super_dependency_graph import generate_super_dependency_graph_from_theory
from lib.atom_set import AtomSet
from lib.logic import has_OSH_property
import lib.logic
import argparse
import time
import sys
from lib.logic_program import Rule, DisLP
from lib.clause_theory import ClauseTheory

def main_algorithm(T: 'ClauseTheory', M: 'AtomSet', check_osh: bool = False):
    G = generate_super_dependency_graph_from_theory(T)
    G.remove_empty_sources()

    has_osh = True

    while True:
        #print(M)
        # TODO: runtime
        #print(G)
        if check_osh and not G.is_empty():
            has_osh = has_osh and has_OSH_property(T, G)
        S = G.get_S_with_property(T, M)        
        #print(S)
        if S is None:
            # no source with the required property
            break

        
        
        # easy steps from algorithm having polinomial runtime
        X = M.intersection(S)
        M = M.difference(X)
        T.reduce(X, S.difference(X))
        G = generate_super_dependency_graph_from_theory(T)
        G.remove_empty_sources()
    
    if check_osh:
        return (len(M) == 0, has_osh)
    else:
        return len(M) == 0

def minimality_check(T: 'ClauseTheory', M: 'AtomSet'):
    # M: a minimal model of Sigma 
    SG =  generate_super_dependency_graph_from_theory(T)
    ## b_SG  = copy.deepcopy(SG) ## keep it for computing the previous dependency nodes, a simple way is to use all 
    DS=AtomSet()  # the established atoms
    SG.remove_empty_sources() ## remove all empty sources
    sources = SG.get_sources()
    while len(sources) > 0:
        S = list(sources)[0]
        SA = S.get_atoms()
        T.reduce_cb(DS)
        TC = ClauseTheory()
        found = False
        for cl in T:
            if len(SA)==1 and cl.get_positive() == SA and cl.len_negative() == 0:
                found = True
                break
            if cl.get_atoms().difference(SA).is_empty():
                TC.add_clause(cl)
        if not found and not lib.logic.is_minimal_model(TC, SA): return False

        DS = DS.union(SA)
        SG.remove_node(S)
        SG.remove_empty_sources()
        sources = SG.get_sources()
    return DS.difference(M).is_empty()

def usage():
    print("usage: {0} file_cnf file_model [--check-osh]".format(sys.argv[0]))
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CheckMin, a minimal model checking algorithm')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-TT_OLD", help="use enumeration algorithm for consequence checking",action = "store_true")
    group.add_argument("-TT_SAT", help="use sat solver for consequence checking (large overhead for file generation", action = "store_true")
    group.add_argument("-TT_PYSAT", help="use pysat package with glucose4 for consequence checking", action = "store_true")
    parser.add_argument("file_CNF", help = "theory file")
    parser.add_argument("file_M", help = "model file")
    parser.add_argument("--check_osh", action='store_true', help="check for the one-source-head property")
    parser.add_argument("-lp", help="The theory file is a logic program", action='store_true',default=False)
    parser.add_argument("-v2", help="The new minimality check algorithm", action='store_true',default=False)
    args = parser.parse_args()
    check_osh = False
    try:
        if args.TT_OLD:
            lib.logic.TT_sel = "TT_OLD"
        elif args.TT_SAT:
            lib.logic.TT_sel = "TT_SAT"
        elif args.TT_PYSAT:
            lib.logic.TT_sel = "TT_PYSAT"
        dlp = DisLP()
        if not args.lp:
            clause_theory = cnf_parser(args.file_CNF)
            model = model_parser(args.file_M)
        else: # input logic program and its answer set
            dlp.build_DLP(args.file_CNF)
            model = model_parser(args.file_M, dlp)
            v_dlp = dlp.GL_reduct(model)
            clause_theory = v_dlp.To_ClauseTheory()
        check_osh = args.check_osh
    except FileNotFoundError as e:
        print(e)
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)
    
    all_atom_nums = clause_theory.get_all_atom_nums()
    for atom in model:
        if not atom in all_atom_nums:
            print("model uses an atom which does not exist in given theory")
            exit(1)
    #clause_theory.reduce(AtomSet(), AtomSet({2}))
    #clause_theory.reduce(AtomSet({1}), AtomSet())
    #clause_theory.reduce(AtomSet(), AtomSet({5, 6}))
    #model = AtomSet({4})
    clause_theory, _ids = clause_theory.minimal_reduct(model)
    try:
        start = time.time()
        if not args.v2:
            res = main_algorithm(clause_theory, model, check_osh)
        else:
            res = minimality_check(clause_theory, model)
        end = time.time()
        print(end-start)
        if check_osh:
            is_min_model = res[0]
            print("OSH" if res[1] else "NO OSH")
        else:
            is_min_model = res
        if is_min_model:
            print("YES")
        else:
            print("NO")
        
    except ValueError as e:
        print(e)
