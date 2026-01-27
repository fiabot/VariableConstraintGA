import matplotlib.pyplot as plt
import numpy as np 
import statistics
import jsonpickle 


folder =  "TTP"
persona = "Adaptive"
trials= 25
qd_scores= {} 
colors = ["#8A4F7D", "#011638", "#88A096", "#EF8275",  "#FFD2FC"]
lines = ["solid", "dotted", "dashed", "dashdot"]


folders = {"TTP": "TTP", "Logic Grid Puzzles": "LogicPuzzles", "Lode Runner Levels": "LodeRunner"}
personas = {"Adapt": "Adaptive", "Explore":"Exploratory", "Strict":"Strict", "Cycle": "TwoForward"}


algos = ["Filtering", "Restarts", "Shuffling", "VCMap" ] 
plt.rcParams.update({'font.size': 18})

import matplotlib as mpl

mpl.rcParams['lines.linewidth'] = 2.5
mpl.rcParams['lines.linestyle'] = '--'


for folder in folders:
    for persona in personas:
        for algo in algos:
            values = [] 
            for i in range(25):
                file = folders[folder] + "/" + personas[persona] + "/" + algo + "/trial" + str(i) + ".json" 

                text = open(file, "r").read()
                measures = jsonpickle.decode(text)


                scores = measures["qd_score"] 

                for j, score in enumerate(scores):
                    if  len(values) < j + 1:
                        values.append([])
                    values[j].append(score)
            qd_scores[algo] = values 
                
        for j, alg in enumerate(algos):
            means = np.array([statistics.mean(i) for i in qd_scores[alg]])
            stds = np.array([statistics.stdev(i) for i in qd_scores[alg]])
            x = np.arange(len(means))
            plt.plot(x, means, linestyle=lines[j], color=colors[j], label=alg)
            #plt.fill_between(x, means - stds, means+ stds, color=colors[j], alpha=0.1)


        plt.title("{} with {} Persona".format(folder, persona))
        plt.ylabel("Avg QD-Score")
        plt.xlabel("Generation")
        if persona == "Adapt" and folder == "Logic Grid Puzzles":
            plt.legend()
        plt.show()