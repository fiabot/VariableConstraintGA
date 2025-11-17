import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 

import random 

from GeneticAlgorithmInterface import User
from ProblemSpaceInterface import ProblemSpace 

class AdaptiveUser(User):
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        cur_constraints = cur_constraints[:]

        # Algorithm gave a recommendations 
        if not recommendation is None:
            try: 
                cur_constraints.remove(recommendation)
                return cur_constraints, True, True 
            except: 
                print("ALGORITHM GAVE BAD RECOMMENDATION")
        
        else:
            bin_to_pick = [fes for fes in feasible if len(fes) > 0]

            if len(bin_to_pick) == 0:
                return cur_constraints, False, False 
            bin_picked = random.choice(bin_to_pick)
            indv_picked = random.choice(bin_picked)

            new_con = self.problem_space.get_ind_constraint(indv_picked[1])

            return cur_constraints + [new_con], True , False 

