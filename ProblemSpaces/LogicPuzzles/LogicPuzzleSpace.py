import sys
import os 
from pathlib import Path
import math 


sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from ProblemSpaceInterface import ProblemSpace, Constraint
from LogicPuzzle import Puzzle, Category
from HintGrammar import HintSet, generate_hint
from Constraints import get_constant_constraints, random_constraint, constraint_in_ind, is_contradictory
import random 

order = Category("order", ["1st", "2nd", "3rd", "4th"], True)
method = Category("method", ["whole", "halved", "chopped", "mashed"], False)
ingredient = Category(
    "ingredient", ["Potatoes", "Carrots", "Mushrooms", "Onions"], False
)

SOUP_PUZZLE = Puzzle([order, method, ingredient])


class LogicPuzzleSpace (ProblemSpace):
    def __init__(self, basePuzzle = None): 
        if basePuzzle is None:
            basePuzzle = SOUP_PUZZLE
        self.basePuzzle = basePuzzle 

    def generate_random_individual(self):
        num = random.randint(1, 5)
        hints = [generate_hint(self.basePuzzle) for i in range(num)]
        return HintSet(hints, self.basePuzzle)

    def mutate(self, individual, mutation_rate):
        return individual.mutate(mutation_rate)

    def cross_over(self, ind1, ind2):
        return ind1.cross_over(ind2)  
    
    def fitness(self, individual): 
        return 15 - min(individual.hint_size(),15)
    
    def get_num_bins(self):
        return 8 
    
    def place_in_bin(self, ind):
        return min(ind.solver_loops() - 1, 7)

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