

from ProblemSpaceInterface import ProblemSpace

class Measures:
    """
    Capture values throughout 
    the evolution process 
    """
    def __init__(self):
        self.populations = []
        self.diversity = [] 
        self.constraint_size = [] 
        self.adaptability = [] 
        self.robustness = [] 
        self.advisability = [] 
        self.quality = [] 
        self.qd_score = [] 
    
    def add_adaptability(self, old_pop, new_pop):
        old_num_bins = len([bi for bi in old_pop if len(bi) > 0])
        old_div = old_num_bins / len(old_pop)

        new_num_bins = len([bi for bi in new_pop if len(bi) > 0])
        new_div = new_num_bins / len(new_pop)

        score = (new_div - old_div) / old_div if old_div != 0 else 0 

        self.adaptability.append(score)
    
    def add_gen(self, population, constraint_size, made_change, followed_rec):
        self.populations.append(population)
        

        fitnesses = [element[0][0] for element in population if len(element) > 0]

        self.qd_score.append(sum(fitnesses))


        if len(fitnesses) > 0:
            self.quality.append(sum(fitnesses) / len(fitnesses))
        else:
            self.quality.append(-1)
        num_bins = len([bi for bi in population if len(bi) > 0])
        new_div = num_bins / len(population)

        if len(self.populations) > 1:

            old_size = self.constraint_size[-1]
            old_div = self.diversity[-1]
            score = (new_div - old_div) / new_div if new_div != 0 else 0  
            
            if made_change:
                if old_size > constraint_size:
                    self.robustness.append(score)

            if followed_rec:
                self.advisability.append(score)
        
        self.diversity.append(new_div)
        self.constraint_size.append(constraint_size)


class User:
    """
    This is an interface for a procedural 
    persona that reacts to evolution over arbitrary 
    problem spaces 
    """
    def __init__(self, problem_space: ProblemSpace):
        self.problem_space = problem_space
    
    def update_constraints(self, cur_constraints, feasible, recommendation = None):
        return [], False, False 

class VariableConstraintGA:
    """
    Interface for a variable constraint 
    genetic algorithm 
    """
    def __init__(self, problem_space: ProblemSpace, number_generations, population_size, max_memory, cross_over_rate, mutation_rate, user, update_interval):
        self.problem_space = problem_space
        self.number_generations = number_generations 
        self.population_size = population_size 
        self.max_memory = max_memory 
        self.cross_over_rate = cross_over_rate
        self.mutation_rate = mutation_rate
        self.user = user 
        self.made_change = False 
        self.followed_rec = False 
        self.update_interval = update_interval 
    
    def reset(self):
        """
        Reset environment for next run 

        Should NOT be over-written 
        """
        self.variable_constraints = self.problem_space.get_initial_variable_constraints()
        self.measure_history = Measures()

    def set_up(self):
        """
        Run at the start of each run 

        Can be over-written by child 
        """
        pass 
    
    def record_gen(self, population, recommendation, new_constraints, made_change, followed_rec):
        """
        Record outcomes from a single generation 

        Should NOT be over-written 
        """
        self.measure_history.add_gen(population, len(new_constraints),made_change,  followed_rec)

    def run_one_generation(self, cons_changed): 
        """
        Complete a single generation of the algorithm

        Returns the population of valid (by both constant and variable constraints)
        individuals that are shorted in bins. Each individual should be stored as a tuple
        with the first value being the fitness and the second being the object 

        EX: [[(fit1, obj1)], [], [(fit2, obj2), (fit3, obj3)], .... ] 
        
        NEEDS to be over-written 
        """
        return [] * self.problem_space.get_num_bins() , None 
    
    def run(self):
        """
        Run the full evolution cycle 

        Should NOT be over-written 
        """
        self.reset()
        self.set_up()
        constraints_add_this_cycle = False 
        old_pop = [[]]

        for gen in range(self.number_generations):
            population, recommendation = self.run_one_generation(self.made_change)

            # if interval is met, ask user to update 
            if gen % self.update_interval == 0:
                # end of old cycle 
                if constraints_add_this_cycle:
                    self.measure_history.add_adaptability(old_pop, population)

                variable_constraints , made_change, followed_rec  = self.user.update_constraints(self.variable_constraints[:], population, recommendation)

                # beginning of new cycle 
                old_pop = population 
                constraints_add_this_cycle = len(self.variable_constraints) < len(variable_constraints)
            else:
                followed_rec = False 
                made_change = False 
            self.record_gen(population, recommendation, self.variable_constraints, self.made_change, self.followed_rec)
            self.made_change = made_change
            self.followed_rec = followed_rec 
            self.variable_constraints = variable_constraints
        
        return population