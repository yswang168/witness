from lib.parser import cnf_parser, model_parser
from lib.super_dependency_graph import generate_super_dependency_graph_from_theory
from lib.atom_set import AtomSet
from lib.logic import has_OSH_property, is_minimal_model
import lib.logic
import argparse
import time
import sys

def usage():
    print("usage: {0} file_cnf file_model".format(sys.argv[0]))
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run IsMinModel, a model checking algorithm')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-TT_OLD", help="use enumeration algorithm for consequence checking",action = "store_true")
    group.add_argument("-TT_SAT", help="use sat solver for consequence checking (large overhead for file generation", action = "store_true")
    group.add_argument("-TT_PYSAT", help="use pysat package with glucose4 for consequence checking", action = "store_true")
    parser.add_argument("file_CNF", help = "theory file")
    parser.add_argument("file_M", help = "model file")
    args = parser.parse_args()

    try:
        if args.TT_OLD:
            lib.logic.TT_sel = "TT_OLD"
        elif args.TT_SAT:
            lib.logic.TT_sel = "TT_SAT"
        elif args.TT_PYSAT:
            lib.logic.TT_sel = "TT_PYSAT"
        clause_theory = cnf_parser(args.file_CNF)
        model = model_parser(args.file_M)
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
        res = is_minimal_model(clause_theory, model)
        end = time.time()
        print(end-start)
        is_min_model = res
        if is_min_model:
            print("YES")
        else:
            print("NO")
        
    except ValueError as e:
        print(e)
