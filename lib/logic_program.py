# -*- coding: UTF-8 -*-
from .atom_set import AtomSet 
import copy
from .clause_theory import ClauseTheory
from .clause import Clause

def get_atom_list(atoms_str:'str') -> 'list':
# get a list of atoms from the string a_str seperated by ','
# p(0,1), q(1,2), not  r
    if atoms_str == "": return list()
    p_atoms = []
    n_atoms = []
    tl_str = list(atoms_str)
    nl = 0 # the number of left parenthesis (
    atom = ""
    neg = False
    while len(tl_str) > 0:   
        if tl_str[0] == ' ': 
            tl_str.pop(0)
            continue
        if tl_str[0:4] == list("not "): 
            neg = True
            tl_str.pop(0)
            tl_str.pop(0)
            tl_str.pop(0)
            continue
        
        if tl_str[0] == '(': nl += 1
        if tl_str[0] == ')': nl -= 1
        if tl_str[0] == ',' and nl == 0: 
            if neg: 
                n_atoms += [atom]
            else:
                p_atoms += [atom]
            neg = False
            nl = 0                 
            atom = ""
            tl_str.pop(0)
            continue
        atom += tl_str.pop(0)
    
    if neg:
        n_atoms += [atom]
    else:
        p_atoms += [atom]
        
    #print(atoms_str)
    #print(p_atoms, n_atoms)
    return (p_atoms, n_atoms)
        
        
    

class Rule: 

	def __init__(self, Hr: 'AtomSet', P:'AtomSet'=None, N:'AtomSet'=None):		 
		if Hr == None:
			self.__pos = AtomSet()
			self.__neg = AtomSet()
			self.__head = AtomSet()
			return
		if P != None and N != None:
			self.__pos = AtomSet(P)
			self.__neg = AtomSet(N)
			self.__head = AtomSet(Hr)
		else:
			self.__pos = Hr.get_pos()
			self.__neg = Hr.get_neg()
			self.__head = Hr.get_head()

	def __eq__(self, other: 'Clause') -> bool:
		if( 
            self.__class__ == other.__class__ and
            self.get_pos() == other.get_pos() and
            self.get_neg() == other.get_neg() and
			self.get_head() == other.get_head()
        ):
			return True
		else:
			return False

	def __hash__(self) -> int:
		return hash((frozenset(self.get_head()), frozenset(self.get_pos()), frozenset(self.get_neg())))

	def __copy__(self) -> 'Rule':
		return Rule(copy.copy(self.get_Head()), copy.copy(self.get_pos()), copy.copy(self.get_neg()))

	def __repr__(self) -> str: 
		h = ' | '.join(map(str, self.get_head()))
		p = ' , '.join(map(str,self.get_pos()))
		n = ' , '.join(map(lambda x: str(-x), self.get_neg()))
		if len(p)+len(n) == 0:
			return h + "."
		else:
			if len(p) > 0:
				h = h+ " :- " + p
				if len(n) > 0: 
					h = h+" , " + n
			else:
				if len(n) > 0:
					h = h + " :- " + n
			return h+"." 
	
	def rule_in_atoms_names(self, to_atom_set:'dictionary') -> str:
		hd = [to_atom_set[x] for x in self.__head]
		pos = [to_atom_set[x] for x in self.__pos]
		neg = [to_atom_set[x] for x in self.__neg]
		h = ' | '.join(hd)
		p = ' , '.join(pos)
		n = ' , '.join(map(lambda x: "not "+ x, neg))
		if len(p)+len(n) == 0:
			return h + "."
		else:
			if len(p) > 0:
				h = h+ " :- " + p
				if len(n) > 0: 
					h = h+" , " + n
			else:
				if len(n) > 0:
					h = h + " :- " + n
			return h+"." 

	def get_pos(self):
		return self.__pos

	def get_neg(self):
		return self.__neg

	def get_head(self):
		return self.__head

	def build_rule(self, rule: 'str', AtomMap: 'dictionary'):
		AM = AtomMap
		t = rule.strip('. ').split(":-")
		h = [x.strip() for x in t[0].split('|')]
		for at in h:
			at_id = AM.setdefault(at, len(AM)+1)
			self.__head.add(at_id)
		if len(t) > 1: 
			# b = t[1].split(',') # this is a bug for atoms can be of the form p(a,10) etc. by Yisong, 2020.1.15
			# parse atoms
			(pa, na) = get_atom_list(t[1])
			for i in range(len(pa)):
				at_id = AM.setdefault(pa[i],len(AM)+1)
				self.__pos.add(at_id)
			for i in range(len(na)):
				at_id = AM.setdefault(na[i],len(AM)+1)
				self.__neg.add(at_id)
            
		return (self,AM)

class DisLP:
	def __init__(self, dlp: 'DisLP' = None):
		if dlp == None:
			self.__rules = set()
			self.__to_atom_set = {}    # ID: Atom_Name dictionary
			self.__from_atom_set = {}  # Atom_Name: ID dictionary
		else:
			self.__rules = set(dlp.get_rules())
			self.__to_atom_set = dlp.get_to_atom_set()
			self.__from_atom_set = dlp.get_from_atom_set()

	def get_rules(self):
		return self.__rules

	def get_to_atom_set(self):
		return self.__to_atom_set

	def get_from_atom_set(self):
		return self.__from_atom_set

	def __iter__(self) -> iter:
		return iter(self.__rules)

	def __len__(self) -> int:
		return len(self.__rules)

	def __eq__(self, other: 'DLP') -> bool:
		if self.__class__ != other.__class__:
			return False
		if len(self.get_rules()) != len(other.get_rules()):
			return False 

		if(set(hash((frozenset(rule.get_head()),frozenset(rule.get_pos()), frozenset(rule.get_neg()))) for rule in self) !=
             set(hash((frozenset(rule.get_head()), frozenset(rule.get_pos()), frozenset(rule.get_nege()))) for rule in other)):
			return False
		return True

	def __repr__(self) -> str: 
		return "\n".join(map(str,self.__rules))

	def print(self):
		for rule in self.__rules:
			print("    "+rule.rule_in_atoms_names(self.__to_atom_set))

	def remove_rule(self, rule):
		self.__rules.remove(rule)

	def add_rule(self, rule):
		self.__rules.add(rule)

# modified to cover internal lparse format
	#def build_DLP_lparse(self, File: 'str'):

	def build_DLP(self, File: 'str'): 
		with open(File,"r") as f:
			lines = f.read().split('\n')
			for i in range(len(lines)):
				if lines[i].strip().find('%')==1: continue  ## the line is comment
				if len(lines[i].replace("\n",'')) == 0: continue ## the line is empty
				r = Rule(None)
				rule, self.__from_atom_set = r.build_rule(lines[i], self.__from_atom_set)
				self.add_rule(rule)
			f.close()
		self.__to_atom_set = {value:key for key, value in self.__from_atom_set.items()}

	def GL_reduct(self,  M: 'AtomSet'):
		RP = DisLP()
		for rule in self.get_rules():
			if rule.get_neg().intersection(M).is_empty():
				RP.add_rule(Rule(rule.get_head(), rule.get_pos(), AtomSet())) 
		RP.__from_atom_set = self.get_from_atom_set()
		RP.__to_atom_set = self.get_to_atom_set()
		return RP


	def MR_reduct(self, M: 'AtomSet'): ### dlp must be positive
		MP = DisLP()
		for rule in self.get_rules():
			if rule.get_pos().difference(M).is_empty():
				MP.add_rule(Rule(rule.get_head().intersection(M), rule.get_pos(), AtomSet())) 
		MP.__from_atom_set = self.get_from_atom_set()
		MP.__to_atom_set = self.get_to_atom_set()
		return MP

	def To_ClauseTheory(self): ### dlp must be positive
		CT = ClauseTheory()
		for rule in self.get_rules(): 
			CT.add_clause(Clause(rule.get_head(), rule.get_pos())) 
		return CT

	def find_GL_MR_rule(self, clause:'Clause', M:'AtomSet') -> Rule:
		for rule in self.__rules:
			if not rule.get_neg().intersection(M).is_empty() \
				or not rule.get_pos().difference(M).is_empty(): # GL-reducted,  MR-reducted
				continue

			if rule.get_head().intersection(M) == clause.get_positive() \
				and rule.get_pos().intersection(M) == clause.get_negative():
				return rule
		return None  # no found

	def find_GL_MR_rules(self, witness:'ClauseTheory', M:'AtomSet'):
		gm_lp = DisLP()
		for clause in witness:
			rule = self.find_GL_MR_rule(clause, M)
			if rule != None:
				gm_lp.add_rule(rule)
		gm_lp.__from_atom_set = self.get_from_atom_set()
		gm_lp.__to_atom_set = self.get_to_atom_set()
		return gm_lp
