import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 

import random 

from GeneticAlgorithmInterface import User
from ProblemSpaceInterface import ProblemSpace 

class ExploratoryUser(User):
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        cur_constraints = cur_constraints[:]
        ## decide to remove constraint 
        if random.random() > 0.5: 
            if len(cur_constraints) == 0:
                return cur_constraints, False, False 
            else: 
                rem = random.choice(cur_constraints)
                cur_constraints.remove(rem)
                return cur_constraints,True, False 
        ## decide to add constraint 
        else: 
            cur_constraints += [self.problem_space.get_rand_constraint()]
            return cur_constraints, True,  False 