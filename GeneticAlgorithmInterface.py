

from ProblemSpaceInterface import ProblemSpace

class Measures:
    def __init__(self):
        self.populations = []
        self.diversity = [] 
        self.constraint_size = [] 
        self.adaptability = [] 
        self.robustness = [] 
        self.advisability = [] 
        self.quality = [] 
    
    def add_gen(self, population, constraint_size, followed_rec):
        self.populations.append(population)

        old_size = self.constraint_size[-1]
        old_div = self.diversity[-1]

        self.constraint_size.append(constraint_size)

        fitnesses = [element.fitness() for innerList in population for element in innerList]
        self.quality.append(sum(fitnesses) / len(fitnesses))

        if len(self.populations) > 1:

            old_size = self.constraint_size[-1]
            old_div = self.diversity[-1]
            
            num_bins = [bi for bi in population if len(bi) > 0]
            new_div = num_bins / len(population)
            
            # lost a constraint 
            if old_size > constraint_size:
                self.robustness.append(new_div - old_div)

            # gained a constraint 
            elif old_size < constraint_size:
                self.adaptability.append(new_div - old_div)
            
            if followed_rec:
                self.advisability.append(new_div - old_div)
        
        self.diversity.append(new_div)


class User:
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        return [], False 

class VariableConstraintGA:
    def __init__(self, problem_space: ProblemSpace, number_generations, population_size, max_memory, cross_over_rate, mutation_rate, user):
        self.problem_space = problem_space
        self.number_generations = number_generations 
        self.population_size = population_size 
        self.max_memory = max_memory 
        self.cross_over_rate = cross_over_rate
        self.mutation_rate = mutation_rate
        self.user = user 
    
    def reset(self):
        self.variable_constraints = self.problem_space.get_initial_variable_constraints()
        self.measure_history = Measures()

    def set_up(self):
        pass 
    
    def record_gen(self, population, recommendation, new_constraints, followed_rec):
        self.measure_history.add_gen(population, len(new_constraints), followed_rec)

    def run_one_generation(self): 
        return [] * self.problem_space.get_num_bins() , None 
    
    def run(self):
        self.reset()
        self.set_up()

        for gen in range(self.number_generations):
            population, recommendation = self.run_one_generation()
            self.variable_constraints , followed_rec  = self.problem_space.update_constraints(self.variable_constraints[:], population, recommendation)
            self.record_gen(population, recommendation, self.variable_constraints, followed_rec)
        
        return population