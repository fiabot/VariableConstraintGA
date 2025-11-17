import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 

import random 

from GeneticAlgorithmInterface import User
from ProblemSpaceInterface import ProblemSpace 

class StrictUser(User):
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        cur_constraints = cur_constraints[:]

        new_con = self.problem_space.get_rand_constraint() 
        i = 0 
        while not self.problem_space.is_contradictory( cur_constraints + [new_con]) and i < 1000:
            new_con = self.problem_space.get_rand_constraint()
            i += 1 
        if not i == 1000:
            cur_constraints += [new_con]
        return cur_constraints, True,  False 