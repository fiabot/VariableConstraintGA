import sys
import os 
from pathlib import Path
import math 
from copy import deepcopy
import numpy as np 
import random
 


sys.path.append(str(Path.cwd().parent.parent)) 
sys.path.append(str(Path.cwd().parent)) 
sys.path.append(str(Path.cwd())) 
from ProblemSpaceInterface import ProblemSpace, Constraint

from ProblemSpaces.TravelingThief.GeneticOperators import random_individual, mutate, cross_over 
from ProblemSpaces.TravelingThief.Utils import fitness  


class WeightConstraint (Constraint):
    def __init__(self, params, nodes,items, ratio=1):
        self.params = params 
        self.nodes = nodes 
        self.items = items 
        self.ratio = ratio 
        super().__init__()
    def apply(self, individual):
        fit = individual.get_fit()

        return fit["total_weight"] < self.params["knapsack_capacity"] * self.ratio

class ItemConstraint(Constraint):
    def __init__(self, index):
        self.index = index 
    
    def apply(self, individual):
        return individual.solution[1][self.index] == 1 


class NullConstraint(Constraint):
    def apply(self, individual):
        return True 


def random_constraint(num_items):
    i =  random.randint(0, num_items -1)

    return ItemConstraint(i)

def rand_constraint_ind(ind):
    indices =  [i for i, val in enumerate(ind.solution[1]) if val == 1]

    if len(indices) == 0:
        return NullConstraint()
    
    i = random.choice(indices)

    return ItemConstraint(i)

def is_contradictory(constraints,items, max_weight):
    indices = []
    weight_sum = 0 
    for con in constraints:
        if isinstance(con, ItemConstraint):
            i = con.index 
            item = items[i]
            weight_sum += item[2]
            if i in indices:
                return True 
            indices.append(i)
    
    return weight_sum <= max_weight

