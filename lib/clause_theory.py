from .clause import Clause
from .atom_set import AtomSet
from itertools import combinations as itercombs
import copy

class ClauseTheory:
    def __init__(self, clauses: 'iterable' = None):
        if clauses == None:
            self.__clauses = set()
        else:
            self.__clauses = set(clauses)
    
    def add_clause(self, clause: Clause):
        self.__clauses.add(clause)

    def get_clause(self, index: int) -> Clause:
        ### return self.__clauses[index]  Changed by Yisong
        return list(self.__clauses)[index] 

    def get_clauses(self) -> list:
        return self.__clauses

    def remove_clause(self, clause):
        self.__clauses.remove(clause)

    # returns all distinct atoms, that appear in the clause theory
    # this is a set of integers
    def get_all_atom_nums(self) -> set:
        atom_set = AtomSet()
        for clause in self.__clauses:
            atom_set.update(clause.get_positive())
            atom_set.update(clause.get_negative())
        return atom_set
    
    def __repr__(self) -> str:
        ### return 'Theory:\n' + '\n'.join(map(str, self.__clauses)) ## Changed by Yisong
        return '\n'.join(map(str, self.__clauses))
    def __iter__(self) -> iter:
        return iter(self.__clauses)

    def __len__(self) -> int:
        return len(self.__clauses)

    def len(self) -> int:
        return len(self.__clauses)

    def __eq__(self, other: 'ClauseTheory') -> bool:
        if self.__class__ != other.__class__:
            return False
        if len(self.get_clauses()) != len(other.get_clauses()):
            return False
        if(set(hash((frozenset(clause.get_positive()), frozenset(clause.get_negative()))) for clause in self) !=
             set(hash((frozenset(clause.get_positive()), frozenset(clause.get_negative()))) for clause in other)):
            return False
        return True
        
    # reduces the clause theory,
    # namely sets all atoms in X to true and all atoms in Y to false
    # more precisely it removes all clauses, which have atoms of X in the head or atoms of Y in the body
    # and then removing all remaining atoms
    def reduce(self, X: AtomSet, Y: AtomSet):
        new_clauses = set()
        XuY = X.union(Y)
        for clause in self:
            if len(clause.get_positive().intersection(X)) != 0:
                # an atom of X is in the head
                continue
            if len(clause.get_negative().intersection(Y)) != 0:
                # an atom of Y is in the body
                continue
            clause.get_positive().difference_update(XuY)
            clause.get_negative().difference_update(XuY)
            new_clauses.add(clause)
        self.__clauses = new_clauses

    # reduces the theory based on a set T
    # -removes all clauses, where an atom from T is part of the head
    # -removes atoms in T from all remaining clauses
    def reduce_cb(self, T: AtomSet):
        # care with hashes here!
        new_clauses = set()
        for clause in self:
            if len(clause.get_positive().intersection(T)) != 0:
                continue
            clause.get_negative().difference_update(T)            
            ### Add by XXXX
            if (clause.len_positive() + clause.len_negative()) > 0 :
                new_clauses.add(clause)            

        self.__clauses = new_clauses

    # returns the minimal reduct of a clause theory
    # removing each clause α from Σ if |α - S| != 0 and
    # removing each atom p in the remaining clauses if p not in S.
    def minimal_reduct(self, S: AtomSet) -> 'ClauseTheory':
        new_clause_theory = ClauseTheory()
        s = set()
        for clause in self:
            if len(clause.get_negative().difference(S))==0:
                new_clause = copy.copy(clause)
                new_clause.get_positive().intersection_update(S)
                if new_clause.len_positive() != 0 or new_clause.len_negative() != 0:
                    # we dont want multiple same clauses
                    val = tuple([tuple(new_clause.get_positive().get_atoms()), tuple(new_clause.get_negative().get_atoms())])
                    if val not in s:
                        s.add(val)
                        new_clause_theory.add_clause(new_clause)

        return new_clause_theory       

    # returns a new clause theory, which only contains atoms from S
    def subset_S(self, S: AtomSet) -> 'ClauseTheory':
        new_clause_theory = ClauseTheory()
        for clause in self:
            if len(clause.get_positive().difference(S)) == 0 and len(clause.get_negative().difference(S)) == 0:
                new_clause_theory.add_clause(copy.copy(clause))
        return new_clause_theory

    # checks if an atomset models every clause in the theory
    def pl_true(self, atom_set: AtomSet) -> bool:
        for clause in self:
            if not clause.satisfied(atom_set):
                return False
        return True

    # checks if the clause theory is positve
    # this means, if all clauses have some atoms in the head
    def is_positive(self) -> bool:
        return all(len(clause.get_positive()) > 0 for clause in self)

    # iterates over all combinations of n clauses of the clause theory
    # and returns a clause theory for every of these combinations
    # O((|self| over n) * n)
    def combinations(self, n: int) -> 'iterable':
        for clauses in itercombs(self.get_clauses(), n):               
            yield ClauseTheory(clauses)

    # returns a clause theory which contains all clauses, which have an index from indices in this clause theory
    # does not copy clauses!
    def from_indices(self, indices: list) -> 'ClauseTheory':
        return ClauseTheory(list(self.__clauses)[i] for i in indices)
        
    ### Yisong
    # get the clauses X in the __clauses such that MR(X,M)=clauses
    def find_MR_clauses(self, clauses: 'ClauseTheory', M: 'AtomSet') -> 'ClauseTheory':
        indices = list()
        for clause in clauses:
            ind = self.find_MR_clause(clause, M) 
            if ind >= 0:
                indices.append(ind)

        return self.from_indices(indices)

    # get the index of the cluase x in the __clauses such that MR(x,M)==clause
    def find_MR_clause(self, clause: 'Clause', M: 'AtomSet') -> 'Clause':
        for i in range(self.len()): 
            _clause = self.get_clause(i)
            if len(clause) > len(_clause): continue
            if _clause.get_positive().intersection(M) == clause.get_positive() and \
                _clause.get_negative() == clause.get_negative():
            #if self.get_clause(i).get_positive().intersection(M) == clause.get_positive() and \
            #    self.get_clause(i).get_negative() == clause.get_negative():
                return i
        return -1
