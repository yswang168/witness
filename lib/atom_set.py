from ordered_set import OrderedSet
class AtomSet:
    def __init__(self, atoms: 'iterable' = None):
        if atoms == None:
            self.__atoms = set()
        else:
            self.__atoms =  set(atoms)
    def get_atoms(self) -> set:
        return self.__atoms

    def __repr__(self) -> str:
        return "AtomSet(atoms: {0})".format(self.__atoms)

    def __iter__(self) -> iter:
        return iter(self.__atoms)

    def __len__(self) -> int:
        return len(self.__atoms)

    def is_empty(self) -> bool:
        return self.__len__() == 0

    def intersection(self, other: 'AtomSet') -> 'AtomSet':
        return AtomSet(self.get_atoms().intersection(other.get_atoms()))

    def difference(self, other: 'AtomSet') -> 'AtomSet':
        return AtomSet(self.get_atoms().difference(other.get_atoms()))

    def add(self, atom: int):
        return self.__atoms.add(atom)
    
    def remove(self, atom: int):
        return self.__atoms.remove(atom)
    
    def difference_update(self, other: 'AtomSet') -> 'AtomSet':
        return self.__atoms.difference_update(other.get_atoms())

    def intersection_update(self, other: 'AtomSet') -> 'AtomSet':
        return self.__atoms.intersection_update(other.get_atoms())

    def union(self, other: 'AtomSet') -> 'AtomSet':
        return AtomSet(self.get_atoms().union(other.get_atoms()))

    def update(self, other: 'AtomSet') -> 'AtomSet':
        return self.get_atoms().update(other.get_atoms())

    def pop(self) -> int:
        return self.__atoms.pop()

    def __eq__(self, other: 'AtomSet') -> bool:
        return (
            self.__class__ == other.__class__ and
            self.get_atoms() == other.get_atoms()
        )
    
    def __copy__(self) -> 'AtomSet':
        return AtomSet(self.__atoms.copy())

    def __contains__(self, item):
        return item in self.get_atoms()

    