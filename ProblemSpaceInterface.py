class Constraint:
    """
    All constraints should inherit this class 
    """
    def __init__(self):
        pass 
    
    def apply(self, individual):
        """
        Given an individual, return 
        true if constraint is obeyed 
        """
        return False 

class ProblemSpace: 
    """
    To add a problem space to this benchmark, 
    create a class that inherits this class as a 
    parent 

    You will need to over-write all methods 
    in this class 
    """
    def __init__(self): 
        pass 

    def generate_random_individual(self):
        '''
        Return a random in individual in the problem space 
        for initialization 
        '''
        return None 

    def mutate(self, individual, mutation_rate):
        '''
        Take in an individual and return a mutation

        Amount of mutation can vary between 0 and 1 from mutation rate 
        e.g. each bit has a X% chance of flipping 

        Should NOT modify starting individual 
        '''
        return None 

    def cross_over(self, ind1, ind2):
        """
        Take in two individuals and return a random combination of the two

        Should NOT modify the starting individuals  

        """
        return None, None 
    
    def fitness(self, ind): 
        """
        Fitness value of an individual. Should be expresses as a maximization function 
        """
        return 0 
    
    def get_num_bins(self):
        """
        Return the number of bins of the diversity measure 
        """
        return 0 
    
    def place_in_bin(self, ind):
        """
        Return an index between 0 and num_bins - 1 
        for which bin the individual should be placed 
        """
        return 0 

    def get_constant_constraints(self):
        """
        Return a list of constraints that 
        all individuals must obey

        These constraints should be ATOMIC rather then general 
        """
        return [] 
    
    def get_initial_variable_constraints(self):
        """
        Return a list of initial variable constraints 
        """
        return [] 
    

    def is_contradictory(self, constraints):
        """
        Given a list of constraints 
        return true if they are inherently 
        contradictory 

        This does NOT need to ensure 
        that an individual could exist with 
        all listed constraints 
        """
        return False  
    
    def get_rand_constraint(self):
        """
        Return a random variable constraint from the 
        problem space 
        """
        return Constraint() 
    
    def get_ind_constraint(self, ind):
        """
        Given an individual, return a random 
        constraint that is is obeys 
        """
        return Constraint()
    

    