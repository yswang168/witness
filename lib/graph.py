
class Graph:
    def __init__(self, nodes: 'iterable' = None):
        if(nodes == None):
            self.__nodes = set()
        else:
            self.__nodes = set(nodes)
    def get_nodes(self) -> set:
        return self.__nodes
    def get_node_count(self) -> int:
        return len(self.__nodes)    
    def __repr__(self) -> str:
        str_list = []
        for node in self.__nodes:
            str_list.append("{0}->{1}\n".format(str(node), ','.join(map(str, node.get_successors()))))
        return ''.join(str_list)
    def add_node(self, node: 'Node'):
        self.__nodes.add(node)
    # removes a node from the graph and also removes predecessor-links from successors
    def remove_node(self, node: 'Node'):
        for nodeprime in node.get_successors():
            nodeprime.get_predecessors().remove(node)
        self.__nodes.remove(node)
    
    def is_empty(self) -> bool:
        return self.get_node_count() == 0


class Node:
    # val is the id of the atom or clause for a node
    # AtomNodes and ClauseNodes can have the same value for val!
    def __init__(self, val: int, predecessors: 'iterable' = None, successors: 'iterable' = None):
        self.__val = val
        if(predecessors == None):
            self.__predecessors = set()
        else:
            self.__predecessors = set(predecessors)
        if(successors == None):
            self.__successors = set()
        else:
            self.__successors = set(successors)
    def get_predecessors(self) -> set:
        return self.__predecessors
    def get_successors(self) -> set:
        return self.__successors
    def add_successor(self, successor: 'Node'):
        self.__successors.add(successor)
    def add_predecessor(self, predecessor: 'Node'):
        self.__predecessors.add(predecessor)
    def add_successors(self, successors: set):
        self.__successors.update(successors)
    def add_predecessors(self, predecessors: set):
        self.__predecessors.update(predecessors)
    def get_val(self) -> int:
        return self.__val
    def __eq__(self, other: 'Node') -> bool:
        return (self.__class__ == other.__class__ and self.__val() == other.get_val())    
    def __hash__(self) -> int:
        return hash(self.__val)
    # sets the setnode for this node
    # the setnode is a node of the superdependency-graph of the graph for this node
    def set_set_node(self, set_node: 'SetNode'):
        self.__set_node = set_node
    def get_set_node(self) -> 'SetNode':
        return self.__set_node

class AtomNode(Node):
    def __init__(self, val: int, predecessors: 'iterable' = None, successors: 'iterable' = None):
        super().__init__(val, predecessors, successors)
    def __repr__(self) -> str:
        return str(self.get_val())

class ClauseNode(Node):
    # AtomNodes and ClauseNodes can have the same value for __val__
    # so we need somethingt to add to this value for hashing such that we dont have the same hash-value for ClauseNodes and AtomNodes
    # this hash_init is the maximum value of an AtomNode and is the same for each ClauseNode in an Graph!
    def __init__(self, val: int, hash_init: int, predecessors: 'iterable' = None, successors: 'iterable' = None):
        super().__init__(val, predecessors, successors)
        self.__hash_init = hash_init    
    def __repr__(self) -> str:
        return "d{0}".format(self.get_val())    
    def __hash__(self) -> int:
        return hash(self.get_val()+self.__hash_init)

# generates a graph from a positive clause theory as described in paper1
def generate_graph_from_theory(clause_theory: 'ClauseTheory') -> 'Graph':
    # get all the values of the atoms in the theory
    nums = clause_theory.get_all_atom_nums()
    if len(nums) > 0:
        # needed for the hash-init for ClauseNodes
        max_num_atom = max(nums)
    # backlink from atom-values to AtomNodes
    node_map = {}
    graph = Graph()
    for num in nums:
        atom_node = AtomNode(num)
        node_map[num] = atom_node
        graph.add_node(atom_node)
    i = 1
    # add the clauses to the graph and also add all the successor- and predecessor-links using the node_map
    for clause in clause_theory:
        clause_node = ClauseNode(i, max_num_atom)
        graph.add_node(clause_node)
        clause_node.add_successors([node_map[num] for num in clause.get_positive()])
        clause_node.add_predecessors([node_map[num] for num in clause.get_negative()])
        for atom in clause.get_positive():
            node_map[atom].add_predecessor(clause_node)
        for atom in clause.get_negative():
            node_map[atom].add_successor(clause_node)
        i+=1
    return graph
