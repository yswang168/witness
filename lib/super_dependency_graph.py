
from .graph import Graph, Node, generate_graph_from_theory, AtomNode
from .atom_set import AtomSet
from .logic import is_minimal_model

class SuperDependencyGraph(Graph):
    # initializes a SuperDependencyGraph with all SetNodes
    # also adds each SetNode with empty predecessors to __sources
    def __init__(self, nodes: 'iterable' = None):
        super().__init__(nodes)
        self.__sources = set()
        if not nodes == None:
            for node in nodes:
                if not node.get_predecessors():
                    self.__sources.add(node)

    def get_sources(self) -> bool:
        return self.__sources

    # adds a node and if its predecessors are empty adds it to __sources
    def add_node(self, node: 'SetNode'):
        super().add_node(node)
        if not node.get_predecessors():
            self.__sources.add(node)
    
    # removes a node and removes all links to other nodes
    # also updates sources
    def remove_node(self, node: 'SetNode'):
        super().remove_node(node)
        for nodeprime in node.get_successors():
            if not nodeprime.get_predecessors():
                self.__sources.add(nodeprime)
        self.__sources.remove(node)
    
    # removes all sources, which only contain ClauseNodes
    def remove_empty_sources(self):
        deleteable_sources = list(source for source in self.__sources if source.is_empty())
        while deleteable_sources:
            source = deleteable_sources.pop()
            self.remove_node(source)
            for node in source.get_successors():
                if not node.get_predecessors() and node.is_empty():
                    deleteable_sources.append(node)  

    # returns a source, for which M intersected with S is a minimal model of T_S
    # TODO: runtime
    def get_S_with_property(self, T, M):
        for source in self.__sources:            
            S = source.get_atoms()
            #print(S, end=" ")
            if(is_minimal_model(T.subset_S(S), M.intersection(S))):
                return S        
        return None



class SetNode(Node):
    def __init__(self, val: int, predecessors: 'iterable' = None, successors: 'iterable' = None, subnodes: 'iterable' = None):
        super().__init__(val, predecessors, successors)    
        if subnodes == None:
            self.__subnodes = list()
        else:
            self.__subnodes = list(subnodes)
    # checks if the node contains no AtomNodes
    def is_empty(self) -> bool:
        return not any(isinstance(subnode, AtomNode) for subnode in self.__subnodes)
    def __repr__(self) -> str:
        return "({0}: {1})".format(self.get_val(), ' '.join(map(str,self.__subnodes)))
    def __eq__(self, other: 'SetNode') -> bool:
        return (self.__class__ == other.__class__ and self.get_val() == other.get_val())
    def __hash__(self) -> int:
        return hash(self.get_val())
    def get_subnodes(self) -> list:
        return self.__subnodes
    # returns all the atoms in the SetNodes as AtomSet
    def get_atoms(self) -> 'AtomSet':
        return AtomSet(subnode.get_val() for subnode in self.__subnodes if isinstance(subnode, AtomNode))


# generates a superdependencygraph from a clause theory as described in paper1 and paper2
def generate_super_dependency_graph_from_theory(clause_theory):
    # first generate a graph
    graph = generate_graph_from_theory(clause_theory)
    # simple kosaraju
    stack = []
    visited = {}
    for node in graph.get_nodes():
        visited[node] = False
    for node in graph.get_nodes():
        dfs(node, stack, visited)
    for node in graph.get_nodes():
        visited[node] = False
    i = 1
    super_dependency_graph = SuperDependencyGraph()
    set_nodes = list()
    # generate setnodes with kosaraju-stack
    while stack:
        node = stack.pop()
        if not visited[node]:
            subnodes = []
            # generate one setnode            
            dfsutil(node, visited, subnodes)
            set_node = SetNode(i, subnodes = subnodes)            
            set_nodes.append(set_node)
            for node in subnodes:
                # set setnode of subnode
                node.set_set_node(set_node)
            i+=1
    # add vertices between setnodes depending on vertices between subnodes
    for node in graph.get_nodes():
        for nodeprime in node.get_successors():
            set_node = node.get_set_node()
            set_nodeprime = nodeprime.get_set_node()
            if set_node == set_nodeprime:
                continue
            set_node.add_successor(set_nodeprime)
            set_nodeprime.add_predecessor(set_node)
    # generate the superdependencygraph
    for set_node in set_nodes:
        super_dependency_graph.add_node(set_node)
    return super_dependency_graph

# simple backwards dfs generating one strongly component
def dfsutil(node: 'SetNode', visited: list, subnodes: list):
    if(visited[node]):
        return
    visited[node] = True
    subnodes.append(node)
    for nodeprime in node.get_predecessors():
        if not visited[nodeprime]:
            dfsutil(nodeprime, visited, subnodes)

# simple dfs in forward direction generating stack for kosaraju
def dfs(node: 'SetNode', stack: list, visited: set):
    if(visited[node]):
        return
    visited[node] = True
    for nodeprime in node.get_successors():
        if not visited[nodeprime]:
            dfs(nodeprime, stack, visited)
    stack.append(node)
