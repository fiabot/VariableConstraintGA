import sys
sys.path.insert(0, "../")  # add Folder_2 path to search list

from ProblemSpaceInterface import ProblemSpace, Constraint
from HintGrammar import HintSet, generate_hint
from Constraints import get_constant_constraints, random_constraint, constraint_in_ind, is_contradictory
import random 

class LogicPuzzleSpace (ProblemSpace):
    def __init__(self, basePuzzle = None): 
        self.basePuzzle = basePuzzle 

    def generate_random_individual(self):
        num = random.randint(1, 5)
        hints = [generate_hint(self.basePuzzle) for i in range(num)]
        return HintSet(hints, self.basePuzzle)

    def mutate(self, individual, mutation_rate):
        return individual.mutate()

    def cross_over(self, ind1, ind2):
        return ind1.cross_over(ind2)  
    
    def fitness(self, individual): 
        return individual.hint_size()
    
    def get_num_bins(self):
        return 10 
    
    def place_in_bin(self, ind):
        return ind.solver_loops()

    def get_constant_constraints(self):
        return get_constant_constraints(self.basePuzzle) 
    
    def get_initial_variable_constraints(self):
        return [] 
    
    def is_contradictory(self, constraints):
        return is_contradictory(self.basePuzzle, constraints) 
    
    def get_rand_constraint(self):
        return random_constraint(self.basePuzzle)
    
    def get_ind_constraint(self, ind):
        return constraint_in_ind(ind)