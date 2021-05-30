from .atom_set import AtomSet
import copy

class Clause:
    #initializes a clause with a set positive and negative literals
    def __init__(self, positive: AtomSet = None, negative: AtomSet = None):
        if positive == None:
            self.__positive = AtomSet()
        else:
            self.__positive = AtomSet(positive)
        if negative == None:
            self.__negative = AtomSet()
        else:
            self.__negative = AtomSet(negative)
    
    #adds a positive literal to the clause
    def add_positive(self, literal: int):
        self.__positive.add(literal)
    
    #adds a negative literal to the clause
    def add_negative(self, literal: int):
        self.__negative.add(literal)

    #removes a positive literal from the clause
    def remove_positive(self, literal: int):
        self.__positive.remove(literal)
    
    #removes a negative literal from the clause
    def remove_negative(self, literal: int):
        self.__negative.remove(literal)

    def set_positive(self, positive: int):
        self.__positive = set(positive)

    def set_negative(self, negative: int):
        self.__negative = set(negative)
    
    def len_positive(self) -> int:
        return len(self.__positive)
    
    def len_negative(self) -> int:
        return len(self.__negative)

    def get_positive(self) -> set:
        return self.__positive

    def get_negative(self) -> set:
        return self.__negative

    def get_atoms(self) ->  AtomSet:
        return self.get_positive().union(self.get_negative())

    def __repr__(self) -> str:
        ### Changed by Yisong
        ### return "{0} -> {1}".format(' and '.join(map(str, self.get_negative())), ' or '.join(map(str, self.get_positive())))
        if self.len_negative() > 0:
            return "  {0} -> {1}".format(' and '.join(map(str, self.get_negative())), ' or '.join(map(str, self.get_positive())))
        else:
            return "  {0}".format(' or '.join(map(str, self.get_positive())))

    def __len__(self) -> int:
        return self.len_positive() + self.len_negative()

    def __eq__(self, other: 'Clause') -> bool:
        if( 
            self.__class__ == other.__class__ and
            self.get_positive() == other.get_positive() and
            self.get_negative() == other.get_negative()
        ):
            return True
        else:
            return False
    
    def __hash__(self) -> int:
        return hash((frozenset(self.get_positive()), frozenset(self.get_negative())))

    def __copy__(self) -> 'Clause':
        return Clause(copy.copy(self.get_positive()), copy.copy(self.get_negative()))

    # returns true iff the clause is satisfied under the atoms in atom_set
    def satisfied(self, atom_set: AtomSet) -> bool:
        if len(self.get_positive().intersection(atom_set)) != 0:
            # an atom of the head is satisfied
            return True
        if len(self.get_negative().difference(atom_set)) != 0:
            # not all atoms of the body are satisfied
            return True
        return False
    



