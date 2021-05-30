
import argparse
import random
import scipy.stats as ss
import numpy as np
import math
#import matplotlib.pyplot as plt

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return ss.truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

def get_clause(bodylength, headlength, choices):
    head = set()
    body = set()
    used = set()
    for _ in range(bodylength):
        atom = random.choice(list(choices.difference(used)))
        used.add(atom)
        body.add(atom)
    for _ in range(headlength):
        atom = random.choice(list(choices.difference(used)))
        used.add(atom)
        head.add(atom)

    return (head, body)

def check_repeat(clauses, clause):
    # checking if the clause is in clauses
    s_clause = sorted(clause)
    for i in range(len(claues)):
        if sorted(clauses[i]) == s_clause:
            return True

    return False

#def generate_theory_simple(c, a, cl):
# the parameters are added by yisong, 2021.2.26
# fl: for fixed clause length
# simple: a simle approach to generate clause
# c...number of clauses
# a...number of atoms
# cl: length of each clause
    #clauses = []
    #ic = 0
    #xclause = 
    #while (ic < c): 
    #    clause = []

# hp...head-to-clauselength ratio as float or the string "UNIFORM"
# hp_std_derivation...head-to-clauselength standard derivation
# cl_std_derivation...clause length standard derivation


def generate_theory(c, a, cl, hp, hp_std_derivation = 0.25, cl_std_derivation = None, fl=False):
    if cl_std_derivation == None:
        cl_std_derivation = cl / 4
    if hp == "UNIFORM":
        uniform_head_lenghts = True
    else:
        uniform_head_lenghts = False
    clauses = []
    atoms = set(range(1, a+1))
    #https://stackoverflow.com/questions/37411633/how-to-generate-a-random-normal-distribution-of-integers
    x = np.arange(-cl+1, cl)
    xU, xL = x + 0.5, x - 0.5 
    if cl_std_derivation != 0:
        prob = ss.norm.cdf(xU, scale = cl_std_derivation) - ss.norm.cdf(xL, scale = cl_std_derivation)
        prob = prob / prob.sum() #normalize the probabilities so their sum is 1
        clause_lengths = np.random.choice(x, size = c, p = prob)+cl
    else:
        clause_lengths = [cl]*c

    if hp != "UNIFORM":
        head_proportions = get_truncated_normal(hp, hp_std_derivation, 0, 1).rvs(c)
    #plt.hist(head_proportions)
    #plt.show()
    #plt.hist(head_lengths, bins = len(x))
    #plt.show()
    #print(sum(head_lengths) / len(head_lengths))
    unused = set(atoms)
    for i in range(c):
        clause_length = clause_lengths[i]
        if uniform_head_lenghts:
            head_length = random.randint(0,clause_length)
        else:
            head_length = int(round(clause_length * head_proportions[i]))
        #print(head_length)
        #head_length = math.ceil(clause_length * head_proportions[i])
        if head_length > clause_length:
            head_length = clause_length
        if len(unused) > 0:
            to_use = set()
            for _ in range(clause_length):
                if len(unused) > 0:
                    to_use.add(unused.pop())
                else:
                    to_use.add(random.choice(list(atoms.difference(to_use))))
        else:
            to_use = atoms
        clauses.append(get_clause(clause_length-head_length, head_length, to_use))
    
    return clauses
    '''if args.dlv:
        for head, body in clauses:
            print(" v ".join(int_to_dlv_var(atom) for atom in head), end = "")
            print(" :- ", end = "")
            print(" , ".join(int_to_dlv_var(atom) for atom in body), end = "")
            print(".")'''

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a testcase')
    parser.add_argument("-c", type = check_positive, help = "number of clauses", required=True)
    parser.add_argument("-a", type = check_positive, help = "number of atoms", required=True)
    parser.add_argument("-cl", type = check_positive, help = "average clause length", required=True)
    parser.add_argument("-hp", type = float, help = "average head/clause proportion", required=True)
    parser.add_argument("-fl", action='store_true', help = "fix the clause length")
    args = parser.parse_args()



    clauses = generate_theory(args.c, args.a, args.cl, args.hp, args.fl)

    print("c average clause length: {0}".format(sum(len(x[0])+len(x[1]) for x in clauses) / len(clauses)))
    print("c average head length: {0}".format(sum(len(x[0]) for x in clauses) / len(clauses)))
    print("p cnf {0} {1}".format(args.a, args.c))
    for head, body in clauses:
        for atom in head:
            print(atom, end=" ")
        for atom in body:
            print(-atom, end=" ")
        print(0)


    
        

        

    
