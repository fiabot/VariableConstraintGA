import sys
import os 
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
sys.path.append(str(Path.cwd().parent) + "/ProblemSpaces/LogicPuzzles") 
from GeneticAlgorithmInterface import VariableConstraintGA
from Algorithms.RandomRestarts import RandomRestarts
from Personas.Exploratory import ExploratoryUser
from Personas.DoNothing import DoNothing 
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace


problem_space = LogicPuzzleSpace()
user = ExploratoryUser(problem_space)
algorithm = RandomRestarts(problem_space, number_generations=100, population_size=50, max_memory=500, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=10)

print(algorithm.run()) 

print(algorithm.infeasible_pop)

for con in problem_space.get_constant_constraints() + algorithm.variable_constraints:
            if not con.apply(algorithm.infeasible_pop[0][1]):
                print("Not Satisfied: ")
                print(con)
            else:
                print("Satisfied: ")
                print(con)

print(algorithm.measure_history.quality)
