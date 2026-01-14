# simple GA to find max of the the two subproblems 

from GeneticOperators import random_individual, mutate, cross_over 
from Utils import read_file, fitness 
import random 
import numpy.random as npr

problem = "problem.ttp"

problems = ["n50_bounded_strongly.ttp", "n50_uncorr_similar.ttp", "n50_uncorr.ttp", "n150_strongly_bounded.ttp", "n150_uncorr_similar.ttp", "n150_uncorr.ttp"]


def roulette_selection(population):
    small = min([c[0] for c in population]) # make all the fitnesses positive 
    if small < 0:
        add = -small 
    else:
        add = 0 
    m = sum([c[0] + add for c in population])
    if m == 0:
        selection_probs = [1 / len(population) for c in population]
    else:
        selection_probs = [(c[0] + add) / m for c in population]
    return population[npr.choice(len(population), p=selection_probs)]

def decide(rate):
    return random.random() < rate


def GA(generations, popsize, x_over_rate, mut_rate, elitism, min, fitness_value, problem):

    population = [] 

    params, nodes, items = read_file(problem)

    def get_fit(ind):
        fit_vals = fitness(params, nodes, items, ind)
        fit = fit_vals[fitness_value]
        if min:
            fit *= -1 
        return fit 
    
 

    for i in range(popsize):
        ind = random_individual(params["cities"], params["num_items"])
        fit = get_fit(ind)
        population.append((fit, ind))

    
    population.sort(reverse=True)

    for gen in range(generations):
        new_pop = population[:elitism] 

        if gen % 100 == 0:
            print("\t\tGeneration: ", gen)
            print("\t\tMax value:", population[0][0])

        while len(new_pop) < popsize:
            par1 = roulette_selection(population)
            par2 =roulette_selection(population)

            if decide(x_over_rate):
                child1, child2 = cross_over(par1[1], par2[1])
            else:
                child1, child2 = par1[1], par2[1]
            
    
            child1 = mutate(child1, mut_rate) 
            child2 = mutate(child2, mut_rate)
          

            new_pop.append((get_fit(child1),child1))
            new_pop.append((get_fit(child2),child2))
        
        population = new_pop
        population.sort(reverse=True) 
    
    return population

if __name__ == "__main__":

    for problem in problems: 
        print("PROBLEM:", problem)
        pop1 = GA(1000, 300, 0.5, 0.1, 50, True, "total_distance", problem)

        print("\tmin Distance:", - pop1[0][0])

        pop2 = GA(1000, 300, 0.5, 0.1, 50, False, "total_distance", problem)

        print("\tmax Distance:", pop2[0][0]) 
        pop3 = GA(1000, 300, 0.5, 0.1, 50, False, "valid_profit", problem)
        print("\tmax profit:",  pop3[0][0])
    
    
