import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
import random 
import math 
import numpy.random as npr

from GeneticAlgorithmInterface import VariableConstraintGA
from ProblemSpaceInterface import ProblemSpace 

def roulette_selection(population):
    m = sum([c[0] for c in population])
    if m == 0:
        selection_probs = [1 / len(population) for c in population]
    else:
        selection_probs = [c[0] / m for c in population]
    return population[npr.choice(len(population), p=selection_probs)]

def decide(rate):
    return random.random() < rate

class VariableConstraintMapElites(VariableConstraintGA):
    def __init__(self, problem_space: ProblemSpace, number_generations, population_size, max_memory, cross_over_rate, mutation_rate, user, update_interval, infeasible_rate = 0.3, elitism = 0.3, height=4):
        self.infeasible_rate = infeasible_rate 
        self.elitism = elitism
        self.height = height 
        super().__init__(problem_space, number_generations, population_size, max_memory, cross_over_rate, mutation_rate, user, update_interval)
    
    def _sort_pop(self, pop):
        pop.sort(key=lambda i: i[0], reverse=True)

    def select_row(self):
        rows = []
        rank = self.height 
        i = 0 
        for row in self.bins:
            non_empty = [l for l in row if len(l) > 0]
            
            # there is at least one child in this row 
            if len(non_empty) > 0:
                rows.append((rank, i))
            
            i += 1 
            rank -= 1 
        
        select = roulette_selection(rows)
        return self.bins[select[1]]
    
    def select(self):
        # select from feasible 
        if decide((self.num_feasible * 2) / (self.num_feasible + len(self.infeasible_pop))):

            # First select the row (based on ranking)
            row = self.select_row()

            # randomly select a bin with children 
            bi = random.choice(range(len(row)))
            while len(row[bi]) == 0:
                bi = random.choice(range(len(row))) 
            
            # select from bin using roulette selection 
            return roulette_selection(row[bi])
        # select from infeasible 
        else:
            return roulette_selection(self.infeasible_pop)


    def place_in_bin(self, ind, infeasible_pop):
        # determine if feasible (from static constraints)
        fes = True 
        constraints_sat = 0 
        for con in self.problem_space.get_constant_constraints():
            if not con.apply(ind):
                fes = False 
            else:
                constraints_sat += 1 
                 
        
        # if feasible put in bin 
        if fes:
            # first determine which row it should be 
            if len(self.variable_constraints) == 0: 
                l = 0 
            else:
                constraints_vio = 0 
                for con in self.variable_constraints:
                    if not con.apply(ind):
                        constraints_vio += 1 
                
                per_vio = constraints_vio / len(self.variable_constraints)
                

                if per_vio == 0:
                    l = 0 
                else:
                    l = math.floor(per_vio * (self.height - 2)) + 1 
            # then determine the column 
            b = self.problem_space.place_in_bin(ind)

            # check if there is room
            if len(self.bins[l][b]) < self.inds_per_bin:
                self.bins[l][b].append((self.problem_space.fitness(ind), ind))
                self._sort_pop(self.bins[l][b])
                self.num_feasible += 1 
            # if individual is better then current ones, replace it 
            elif self.problem_space.fitness(ind) >= self.bins[l][b][-1][0]: 
                self.bins[l][b].pop(-1)
                self.bins[l][b].append((self.problem_space.fitness(ind), ind))
                self._sort_pop(self.bins[l][b])
                self.num_feasible += 1 
        # otherwise put in the infeasible population 
        else:
            # if there is still room in the infeasible fitness add it 
            if len(infeasible_pop) < self.infeasible_pop_size:
                
                infeasible_pop.append((constraints_sat, ind))
    


    def set_up(self):
        self.infeasible_pop_size = self.max_memory * self.infeasible_rate 
        self.elitism_num = round(self.infeasible_pop_size * self.elitism)
        self.feasible_pop_size = self.max_memory - self.infeasible_pop_size 
        self.inds_per_bin = math.floor((self.feasible_pop_size / self.problem_space.get_num_bins())/self.height) 
        self.bins = []
        self.num_feasible = 0 
        self.infeasible_pop = [] 
        
        for j in range(self.height):
            row = []
            for i in range(self.problem_space.get_num_bins()):
                row.append([])
            self.bins.append(row)
        
        # generate initial population 
        for i in range(self.population_size):
            indv = self.problem_space.generate_random_individual()
            self.place_in_bin(indv, self.infeasible_pop)
    
    def satisfies_all_con(self, ind):
        for con in self.problem_space.get_constant_constraints() + self.variable_constraints:
            if not con.apply(ind):
                return False 
        return True 
    
    def clean_bins(self):
        bi = self.bins[:]
        new_bins = [] 
        for li in bi: 
            new_li = [el for el in li if self.satisfies_all_con(el[1])] 
            new_bins.append(new_li)

        return new_bins 

        
    def re_shuffle(self):
        # First get all children from feasible and infeasible pop 
        all_children = self.infeasible_pop[:]
        all_children += [el for row in self.bins for li in row for el in li]

        # then re-set all populations 
        new_infeasible = [] 
        self.set_up()

        #then re-add all children based on new cons 
        for c in all_children:
            self.place_in_bin(c[1], new_infeasible)
        
        self.infeasible_pop = new_infeasible 


    def run_one_generation(self, made_change): 
         # if the constraints have been change, reshuffle population 
        if made_change:
            self.re_shuffle()

        self._sort_pop(self.infeasible_pop)
        new_infeasible = self.infeasible_pop[:self.elitism_num]
        for i in range(math.floor(self.population_size / 2)):
            # select 
            child1 = self.select()[1]
            child2 = self.select()[1]

            # cross over 
            if decide(self.cross_over_rate):
                child1, child2 = self.problem_space.cross_over(child1, child2)
            
            # mutate 
            child1 = self.problem_space.mutate(child1, self.mutation_rate)
            child2 = self.problem_space.mutate(child2, self.mutation_rate)

            # update population 
            self.place_in_bin(child1, new_infeasible)
            self.place_in_bin(child2, new_infeasible)
        
        self.infeasible_pop = new_infeasible 

        return self.bins[0], None 

    