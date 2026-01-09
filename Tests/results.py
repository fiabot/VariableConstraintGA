import jsonpickle
import sys 
import os 
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
sys.path.append(str(Path.cwd().parent) + "/ProblemSpaces/LogicPuzzles")  
folder ="BigTest"
personas = ["Adaptive", "Exploratory", "Strict", "TwoForward"]
algos = ["Filtering", "Restarts", "Shuffling", "VCMap" ]
trials = 50 

stats= {}

for persona in personas:
    print("Persona:", persona)
    for algo in algos:
        qd_scores = []
        adaptive_scores = [] 
        robust_scores = [] 
        last_adaptive = [] 
        last_robust = [] 
        for trial in range(trials):
            file = folder + "/" + persona + "/" + algo + "/trial" + str(trial) + ".json"
            text = open(file, "r").read()
            measures = jsonpickle.decode(text)

            qd_scores += measures.qd_score 
            adaptive_scores += measures.adaptability_qd 
            robust_scores += measures.robustness_qd 

            if len(measures.adaptability_qd) > 0:
                last_adaptive.append(measures.adaptability_qd[-1])
            if len( measures.robustness_qd) > 0: 
                last_robust.append( measures.robustness_qd[-1])
        
        avg_qd = sum(qd_scores) / len(qd_scores) 
        avg_adapt = sum(adaptive_scores) / len(adaptive_scores) if len(adaptive_scores) > 0 else "NA"
        avg_robo = sum(robust_scores) / len(robust_scores) if len(robust_scores) > 0 else "NA"
        avg_la_robo = sum(last_robust) / len(last_robust) if len(last_robust) > 0 else "NA"
        avg_la_adapt = sum(last_adaptive) / len(last_adaptive) if len(last_adaptive) > 0 else "NA"
        print("\tAlgorithm:", algo)

        print("\t\tQD-score:", avg_qd)
        print("\t\tAvg Adapt:", avg_adapt)
        print("\t\tLat adapt:", avg_la_adapt)
        print("\t\tAvg Robust:", avg_robo)
        print("\t\tLast Robo:", avg_la_robo)



            


