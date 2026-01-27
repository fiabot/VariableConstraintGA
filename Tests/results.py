import jsonpickle
import sys 
import os 
from pathlib import Path
import statistics
import json 
from multiprocess import Pool

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir)) 
sys.path.append(str(Path.cwd().parent) + "/ProblemSpaces/LogicPuzzles")  
folder ="LodeRunner"
personas = ["Adaptive", "Exploratory", "Strict", "TwoForward"]
algos = ["Filtering", "Restarts", "Shuffling", "VCMap" ]
trials = 25

stats= {}


def get_data(file):
     
    text = open(file, "r").read()
    measures = jsonpickle.decode(text)
    

    qd_scores = measures.qd_score
    adaptive_scores = measures.adaptability_qd 
    robust_scores = measures.robustness_qd 

    easy_data = jsonpickle.encode({"qd_score":qd_scores, "adaptive_qd":  adaptive_scores , "robustness_qd": robust_scores})
    print("\t\t\t\tfinished trial")
    return easy_data


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

            qd_scores +=  measures["qd_score"]
            adaptive_scores += measures["adaptive_qd"]
            robust_scores += measures["robustness_qd"] 

            if len(measures["adaptive_qd"]) > 0:
                last_adaptive.append(measures["adaptive_qd"][-1])
            if len(measures["robustness_qd"]) > 0: 
                last_robust.append(measures["robustness_qd"][-1])

             
        
        avg_qd = sum(qd_scores) / len(qd_scores) 
        avg_adapt = sum(adaptive_scores) / len(adaptive_scores) if len(adaptive_scores) > 0 else "NA"
        avg_robo = sum(robust_scores) / len(robust_scores) if len(robust_scores) > 0 else "NA"
        avg_la_robo = sum(last_robust) / len(last_robust) if len(last_robust) > 0 else "NA"
        avg_la_adapt = sum(last_adaptive) / len(last_adaptive) if len(last_adaptive) > 0 else "NA"
        print("\tAlgorithm:", algo)

        print("\t\tQD-score:", avg_qd)
        print("\t\t\tstd:", statistics.stdev(qd_scores))
        print("\t\tAvg Adapt:", avg_adapt)
        print("\t\t\tstd:", statistics.stdev(adaptive_scores))
        print("\t\tLat adapt:", avg_la_adapt)
        print("\t\t\tstd:", statistics.stdev(last_adaptive))
        print("\t\tAvg Recovery:", avg_robo)
        print("\t\t\tstd:", -1  if avg_robo == "NA" else statistics.stdev(robust_scores) )
        print("\t\tLast Recovery:", avg_la_robo)
        print("\t\t\tstd:", -1  if avg_robo == "NA" else statistics.stdev(last_robust) )



            


