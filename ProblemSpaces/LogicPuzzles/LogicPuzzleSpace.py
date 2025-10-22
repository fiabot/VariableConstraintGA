import sys
sys.path.insert(0, "../")  # add Folder_2 path to search list

from ProblemSpaceInterface import ProblemSpace, Constraint

class LogicPuzzleSpace (ProblemSpace):
    def __init__(self, basePuzzle = None): 
        self.basePuzzle = basePuzzle 

    def generate_random_individual(self):
        return None 

    def mutate(self, individual, mutation_rate):
        return None 

    def cross_over(self, ind1, ind2):
        return None, None 
    
    def fitness(self): 
        return 0 
    
    def get_num_bins(self):
        return 0 
    
    def place_in_bin(self, ind):
        return 0 

    def get_constant_constraints(self):
        return [] 
    
    def get_initial_variable_constraints(self):
        return [] 
    

    def is_contradictory(self, constraints):
        return False  
    
    def get_rand_constraint(self):
        return Constraint() 