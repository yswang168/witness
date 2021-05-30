import os.path
import logging
from .clause import Clause
from .atom_set import AtomSet
from .clause_theory import ClauseTheory
from .logic_program import Rule, DisLP
import re
from ordered_set import OrderedSet
# parses a file in dimacs-format to a clause-theory
# ignores the p cnf and comment-lines!
# raises ValueError, FileNotFoundError
def cnf_parser(filename: str) -> 'ClauseTheory':
    if not os.path.isfile(filename):
        raise FileNotFoundError("file {0} does not exist".format(filename))
    else:
        file = open(filename)        
        clauses = list()
        clause = Clause()
        i = 0
        for line in file:
            logging.debug("line is {0}". format(line))
            line = line.strip()
            if line == "":
                continue
            line_split = re.split(' |\t', line)

            # check for comment or empty line
            if len(line_split) == 0 or line_split[0] in ("c", "p"):
                continue

            try:
                literals = [int(x) for x in line_split]
                for literal in literals:
                    if literal > 0:
                        clause.add_positive(literal)
                    elif literal < 0:
                        clause.add_negative(-literal)
                    else:
                        clauses.append(clause)
                        clause = Clause()
            except ValueError:
                raise ValueError("invalid value at line {0}".format(i))
            i += 1
        if clause.len_negative() != 0 or clause.len_positive() != 0:
            raise ValueError("last clause not terminated with 0")
        
        return ClauseTheory(clauses)

# parses a file with a list of atoms to an AtomSet
# the file should contain one line containing integers >= 1 separated by one space
# raises FileNotFoundError, ValueError
def model_parser(filename: str, dlp: 'DisLP' = None) -> 'AtomSet':
    if not os.path.isfile(filename):
        raise FileNotFoundError("file {0} does not exist".format(filename))
    else:
        file = open(filename)
        line = file.readline().strip("[]{}\n")
        if not line:
            return AtomSet(set())
        try:
            if dlp == None:
                line = line.replace(',','')
                atoms = OrderedSet([int(x) for x in line.split()])
            else:
                if line.find('{') != -1: ###  dlv output 
                    atoms = line.strip("{}\n").split(", ")
                elif line.find('[') != -1: ### cardical output
                    atoms = line.strip("[]\n").split(", ")
                else:
                    atoms = line.strip().split(" ")
                
                atoms = map(lambda x: x.strip(), atoms)
                atoms = OrderedSet([dlp.get_from_atom_set()[x] for x in atoms])
            return AtomSet(atoms)
        except ValueError:
            raise ValueError("invalid model")



            
