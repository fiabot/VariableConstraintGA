import sys
import os 
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
sys.path.append(str(Path.cwd().parent) + "/ProblemSpaces/LogicPuzzles") 
from GeneticAlgorithmInterface import VariableConstraintGA
from Algorithms.VCMapElites import VariableConstraintMapElites
from Algorithms.Filtering import Filtering
from Algorithms.Shuffling import Shuffling
from Algorithms.RandomRestarts import RandomRestarts 
from Personas.Exploratory import ExploratoryUser
from Personas.DoNothing import DoNothing 
from Personas.Strict import StrictUser 
from Personas.Adaptive import AdaptiveUser
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace
import jsonpickle


NUM_GENS = 300 
POP_SIZE = 100 
MEMORY = 500 
INTERVAL = 50 
TRIALS = 10 
FOLDER = "Experiments/Exploratory"

problem_space = LogicPuzzleSpace()
user = ExploratoryUser(problem_space)
algorithm = VariableConstraintMapElites(problem_space, number_generations=100, population_size=50, max_memory=500, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=10)

trial_info = {"Gens": NUM_GENS, "pop": POP_SIZE, "mem": MEMORY, "intervals":INTERVAL}
file = open(FOLDER + "/info.json", "w")
file.write(jsonpickle.encode(trial_info))
file.close()

# run VC 
for i in range(TRIALS):
    print("VC Map Elites trial:", i)
    
    algorithm = VariableConstraintMapElites(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
    
    algorithm.run() 

    file = open(FOLDER + "/VCMap/trial" + str(i) + ".json", "w")
    file.write(jsonpickle.encode(algorithm.measure_history))
    file.close()

for i in range(TRIALS):
    print("Filtering trial:", i)
    
    algorithm = Filtering(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
    
    algorithm.run() 

    file = open(FOLDER + "/Filtering/trial" + str(i) + ".json", "w")
    file.write(jsonpickle.encode(algorithm.measure_history))
    file.close()

for i in range(TRIALS):
    print("Shuffling trial:", i)
    
    algorithm = Shuffling(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
    
    algorithm.run() 

    file = open(FOLDER + "/Shuffling/trial" + str(i) + ".json", "w")
    file.write(jsonpickle.encode(algorithm.measure_history))
    file.close()

for i in range(TRIALS):
    print("Restarts trial:", i)
    
    algorithm = RandomRestarts(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
    
    algorithm.run() 

    file = open(FOLDER + "/Restarts/trial" + str(i) + ".json", "w")
    file.write(jsonpickle.encode(algorithm.measure_history))
    file.close()
