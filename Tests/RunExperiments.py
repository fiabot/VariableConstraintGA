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
from Personas.TwoForwardOneBack import TwoForOneBackUser
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace
import jsonpickle


NUM_GENS = 500 
POP_SIZE = 200 
MEMORY = 1000 
INTERVAL = 50 
TRIALS = 50 
FOLDER = "BigTest"

problem_space = LogicPuzzleSpace()
trials = {"Exploratory": ExploratoryUser(problem_space), "Adaptive": AdaptiveUser(problem_space), "Strict": StrictUser(problem_space), "TwoForward": TwoForOneBackUser(problem_space)}


for trial in trials:

    user = trials[trial]
    folder = FOLDER + "/" + trial 

    print("RUNNING PERSONA: {}".format(trial))


    #algorithm = VariableConstraintMapElites(problem_space, number_generations=100, population_size=50, max_memory=500, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=10)

    trial_info = {"Gens": NUM_GENS, "pop": POP_SIZE, "mem": MEMORY, "intervals":INTERVAL}
    file = open(folder + "/info.json", "w")
    file.write(jsonpickle.encode(trial_info))
    file.close()

    # run VC 
    for i in range(TRIALS):
        print("\tVC Map Elites trial:", i)
        
        algorithm = VariableConstraintMapElites(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
        
        algorithm.run() 

        file = open(folder + "/VCMap/trial" + str(i) + ".json", "w")
        file.write(jsonpickle.encode(algorithm.measure_history))
        file.close()

    for i in range(TRIALS):
        print("\tFiltering trial:", i)
        
        algorithm = Filtering(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
        
        algorithm.run() 

        file = open(folder + "/Filtering/trial" + str(i) + ".json", "w")
        file.write(jsonpickle.encode(algorithm.measure_history))
        file.close()

    for i in range(TRIALS):
        print("\tShuffling trial:", i)
        
        algorithm = Shuffling(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
        
        algorithm.run() 

        file = open(folder + "/Shuffling/trial" + str(i) + ".json", "w")
        file.write(jsonpickle.encode(algorithm.measure_history))
        file.close()

    for i in range(TRIALS):
        print("\tRestarts trial:", i)
        
        algorithm = RandomRestarts(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.7, mutation_rate=0.5,user=user, update_interval=INTERVAL)
        
        algorithm.run() 

        file = open(folder + "/Restarts/trial" + str(i) + ".json", "w")
        file.write(jsonpickle.encode(algorithm.measure_history))
        file.close()
