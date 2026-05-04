import pymongo 
from bson.objectid import ObjectId
import random 
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
#from ProblemSpaces.LodeRunner.LodeRunnerProblemSpace import LodRunnerProblemSpace
from ProblemSpaces.LogicPuzzles.LogicPuzzleSpace import LogicPuzzleSpace , make_puzzle 
from ProblemSpaces.TravelingThief.TTP_ProblemSpace import TTPProblemSpace 
import jsonpickle 
import pickle 
import gridfs 
import json 



myclient = pymongo.MongoClient("mongodb://localhost:27017/")

db = myclient["QDA-VC-data"] 

users = db["users"]

sessions = db["sessions"]

scenarios = db["scenarios"]

evolveSessions = db["evolveSessions"]
evolveInstances = db["evolveInst"]

evolveBuckets = gridfs.GridFSBucket(db, "evolveAlgorithms")


def get_user_json(id):
    j = {"key": id, "num_sessions":0, "total_time":0, "mode":None, "clicks":[], "evolve_sessions":[], "evolve_instances":[], "scenarios":[]}

    user =  users.find_one({"key":id}) 

    if (user == None):
        return None

    j["mode"] = user["mode"]

    sess = list(sessions.find({"key":id})) 
    j["num_sessions"] = len(sess)

    clicks = []
    total_time = 0
    for s in sess: 
        if not s["totalTime"] is None: 
            total_time += s["totalTime"]
        clicks.append(s["clicks"])
    
    j["total_time"] = total_time 
    j["clicks"] = clicks 

    evolveS = list(evolveSessions.find({"key":id})) 
    for s  in evolveS:
        s["_id"] = str(s["_id"])
    j["evolve_sessions"] = evolveS

    evolveI = list(evolveInstances.find({"key":id})) 
    for s  in evolveI:
        s["_id"] = str(s["_id"])
        file = evolveBuckets.open_download_stream(ObjectId(s["fileId"]))
        contents = file.read()
        algo = pickle.loads(contents)
        qd_score = algo.measure_history.qd_score[-1]
        s["qd-score"] = qd_score 
    j["evolve_instances"] = evolveI

    scens = list(scenarios.find({"key": id}))
    for s  in scens:
        s["_id"] = str(s["_id"]) 
    j["scenarios"] = scens

    return j 

def get_all_keys():
    u = list(users.find({})) 
    u = [user["key"] for user in u]
    return u 

def save_all_with_scen(keys, folder="userData"):
    index =0 
    for key in keys:
        j = get_user_json(key)
        if (not j is None and len(j["scenarios"]) > 0):
            j = json.dumps(j)
            file = open("{}/user_{}.json".format(folder, index), "w")
            file.write(j)
            file.close()
            index += 1 

if __name__ == "__main__":
    print(get_all_keys())

    save_all_with_scen(['Fiona', 'Fiona2'])
