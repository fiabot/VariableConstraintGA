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
from ProblemSpaces.TravelingThief.TTP_ProblemSpace import TTPProblemSpace
import jsonpickle

from multiprocess import Pool


NUM_GENS = 300 
POP_SIZE = 200 
MEMORY = 500 
INTERVAL = 50 
TRIALS = 25 
FOLDER = "TTP"

problem_space = TTPProblemSpace()
trials = {"Exploratory": ExploratoryUser, "Adaptive": AdaptiveUser, "Strict": StrictUser, "TwoForward": TwoForOneBackUser}


def create_trial(user, algo, folder, name):
    def run_trial(i):
        
        problem_space = TTPProblemSpace()
        this_user = user(problem_space)
        algorithm = algo(problem_space, number_generations=NUM_GENS, population_size=POP_SIZE, max_memory=MEMORY, cross_over_rate=0.5, mutation_rate=0.1,user=this_user, update_interval=INTERVAL)
        
        algorithm.run() 

        file = open(folder + "/" + name + "/trial" + str(i) + ".json", "w")
        file.write(jsonpickle.encode(algorithm.measure_history))
        file.close()
        print("\t" + name + "trial:", i)
    return run_trial 

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
    trial_fun = create_trial(user,VariableConstraintMapElites, folder, "VCMap")

    with Pool(1) as p:
        p.map(trial_fun, list(range(TRIALS)))

    # run filtering  
    trial_fun = create_trial(user,Filtering, folder, "Filtering")

    with Pool(1) as p:
        p.map(trial_fun, list(range(TRIALS)))
    
     # run shuffling  
    trial_fun = create_trial(user,Shuffling, folder, "Shuffling")

    with Pool(1) as p:
        p.map(trial_fun, list(range(TRIALS)))
    

     # run shuffling  
    trial_fun = create_trial(user,RandomRestarts, folder, "Restarts")

    with Pool(1) as p:
        p.map(trial_fun, list(range(TRIALS)))


