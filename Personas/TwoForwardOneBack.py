import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 

import random 

from GeneticAlgorithmInterface import User
from ProblemSpaceInterface import ProblemSpace 

class TwoForOneBackUser(User):
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
        self.last_move = "Back"
        self.next_move = "Forward"
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        cur_constraints = cur_constraints[:]

        ## decide to remove constraint 
        if self.next_move == "Back": 
            if len(cur_constraints) == 0:
                to_return = cur_constraints, False, False 
            else: 
                del cur_constraints[0]
                to_return  = cur_constraints,True, False 
        ## decide to add constraint 
        else: 
            new_con = self.problem_space.get_rand_constraint() 
            #while not self.problem_space.is_contradictory( cur_constraints + [new_con]):
            #    new_con = self.problem_space.get_rand_constraint()
            cur_constraints += [new_con]
            to_return = cur_constraints, True,  False 

        if self.next_move == "Forward" and self.last_move == "Forward":
            self.next_move = "Back"
        elif self.next_move == "Back":
            self.next_move = "Forward"
        
        self.last_move = self.next_move 
        return to_return 