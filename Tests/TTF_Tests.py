import sys
import os 
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
sys.path.append(str(Path.cwd().parent) + "/ProblemSpaces/pcg_benchmark_variable_containt") 
from GeneticAlgorithmInterface import VariableConstraintGA
from Algorithms.Shuffling import Shuffling 
from Personas.Exploratory import ExploratoryUser
from Personas.DoNothing import DoNothing 
from Personas.Strict import StrictUser 
from Personas.Adaptive import AdaptiveUser
from ProblemSpaces.TravelingThief.TTP_ProblemSpace import TTPProblemSpace


problem_space = TTPProblemSpace()
user = AdaptiveUser(problem_space)
algorithm = Shuffling(problem_space, number_generations=100, population_size=100, max_memory=500, cross_over_rate=0.5, mutation_rate=0.1,user=user, update_interval=30)

print(algorithm.run()) 


for con in problem_space.get_constant_constraints() + algorithm.variable_constraints:
            
            if not con.apply(algorithm.infeasible_pop[0][1]):
                print("Not Satisfied: ")
                print(con)
            else:
                print("Satisfied: ")
                print(con)



print("Quality")
print(algorithm.measure_history.qd_score)

print("Quality")
print(algorithm.measure_history.quality)

print("\n\nDiversity")
print(algorithm.measure_history.diversity)

print("\n\nAdaptability")
print(algorithm.measure_history.adaptability_qd)

print("\n\nRobustness")
print(algorithm.measure_history.robustness_qd)