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



myclient = pymongo.MongoClient("mongodb://localhost:27017/")

db = myclient["QDA-VC-data"] 

users = db["users"]

sessions = db["sessions"]

scenarios = db["scenarios"]

evolveSessions = db["evolveSessions"]
evolveInstances = db["evolveInst"]

evolveBuckets = gridfs.GridFSBucket(db, "evolveAlgorithms")

DEFAULT_SETTINGS = {"logicPuzzles":{
    "interval": 25, 
    "x-over": 0.7, 
    "mutation": 0.5, 
    "pop_size": 200, 
    "max_memory": 1000 
}}

def get_user(user_id):
    user = users.find_one({"key": user_id})
    return user 

def create_user(key, time):
    if get_user(key) is None:
        mode = random.choice(["filter", "shuffle", "vc-map", "restarts"])
        problem_space = "logicPuzzles"
        
        user_template = {
            "mode": mode,
            "key": key,
            "startTime": time, 
            "totalTime": 0, 
            "likedIndividuals": [],
            "clicks":[],
            "problemSpace": problem_space
        }
        i = users.insert_one(user_template)

        return i
    else:
        return None 
    
def create_scenario(key, time, space_data): 
    if (get_user(key) != None):
        scenario = {
            "key": key, 
            "created": time, 
            "last_updated": time, 
            "data": space_data,
            "evolve_sessions": [] 

        }

        new_scen = scenarios.insert_one(scenario)

        return str(new_scen.inserted_id) 
    else: 
        return None 

def update_scenario_data(key, scenario_id, time, data):
    if (get_user(key) != None):
        scen = scenarios.find_one_and_update({"key": key, "_id": ObjectId(scenario_id)}, {"$set": {"last_updated":time, "data": data}})
        if scen != None:
            return "success"
        else:
            return None 
    else:
        return None 

def get_scenarios(key):
    scens = scenarios.find({"key": key}).to_list()

    for s in scens:
        s["_id"] = str(s["_id"])
    
    return scens 

def get_num_puzzles(outcome):
    num = 0 
    for row in outcome:
        num += len(row)
    return num  

def qd_score(outcome):
    qd = 0 
    for row in outcome:
        if (len(row) > 0):
            qd += row[0][0]

    
def outcome_to_json(outcome, problem_space):
    new_out = [] 
    for row in outcome:
        new_row = [] 
        for ind in row: 
            ind2 = problem_space.to_json(ind[1])
            new_row.append(ind2)
        new_out.append(new_row)
    return new_out 


def create_evolve_start(key, time, cons, scenarioInstance): 
    user = get_user(key)

    if not user is None:
        scen = scenarios.find_one({"key": key, "_id": ObjectId(scenarioInstance)})
        
        if scen is None:
            return None 
        # Set up settings 
        mode = user["mode"]
        spaceName = user["problemSpace"]

        settings = DEFAULT_SETTINGS[spaceName]

        if spaceName == "logicPuzzles":
            puzzle = make_puzzle(scen["data"])
            problemSpace = LogicPuzzleSpace(basePuzzle=puzzle)
        
        print(mode)
        if mode == "filtering":
            algo = Filtering
        elif mode == "shuffling": 
            algo = Shuffling 
        elif mode == "restarts":
            algo = RandomRestarts 
        else: 
            algo = VariableConstraintMapElites
        
        
        # create and run algorithm 
        algorithm = algo(problem_space=problemSpace, number_generations=50, population_size=settings["pop_size"],
                         max_memory=settings["max_memory"], cross_over_rate=settings["x-over"], mutation_rate=settings["mutation"], user=None, 
                         update_interval=settings["interval"])

        
        new_cons = [problemSpace.json_to_constraint(con["con"]) for con in cons if not con is None]
        print("constraints")
        print(cons)
        algorithm.set_up_run() 
        outcome = algorithm.run_interval(new_cons)
        print("outcome")
        print(outcome)


       # Dump pickle file into bucket  
        algo_rep = pickle.dumps(algorithm)

        file_id = ""
        with evolveBuckets.open_upload_stream(key + "-" + str(time)) as grid_in:
            grid_in.write(algo_rep)
            file_id = str(grid_in._id)
        
        # create an evolve session 
        session_data = {
            "key": key, 
            "scenario": scenarioInstance, 
            "startId": file_id, 
            "lastId": file_id,
            "startTime":time, 
            "likedInds": [], 
            "nextIdx": 0
        }

        session = evolveSessions.insert_one(session_data)
        sessionId =  str(session.inserted_id)

        # Add evolve instance and return id 
        data = {
            "key": key, 
            "startTime": time, 
            "sessionCount": 0, 
            "fileId": file_id, 
            "cons": cons ,
            "sessionId": sessionId, 
            "numberPuzzles": get_num_puzzles(outcome), 
            "qd-score": qd_score(outcome), 
            "children": [] 
        }

        evolveInstances.insert_one(data)

        # update scenario 
        scenarios.find_one_and_update({"key": key, "_id": ObjectId(scenarioInstance)}, {"$push":{"evolve_sessions": sessionId}})


        return {"id": file_id, "output": outcome_to_json(outcome, problemSpace), "sessionId": sessionId}  

def continue_evolution(key, time, cons, file_id):
    # Get old instance 
    inst = evolveInstances.find_one({"fileId": file_id, "key": key})

    if inst is None:
        return None

    sessionId = inst["sessionId"] 
    # Get algorithm 
    file = evolveBuckets.open_download_stream(ObjectId(file_id))
    contents = file.read()
    algo = pickle.loads(contents)


    #run algorithm 
    problemSpace = algo.problem_space 
    new_cons = [problemSpace.json_to_constraint(con["con"]) for con in cons if not con is None]
    outcome = algo.run_interval(new_cons)

    # Dump algorithm 
    algo_rep = pickle.dumps(algo)
    new_file_id = ""
    with evolveBuckets.open_upload_stream(key + "-" + str(time)) as grid_in:
        grid_in.write(algo_rep)
        new_file_id = str(grid_in._id)
    
    # Add involve instance and return Id 
    data = { 
            "key": key, 
            "startTime": time, 
            "sessionCount": inst["sessionCount"] + 1, 
            "fileId": new_file_id, 
            "cons": cons , 
            "sessionId": sessionId, 
            "numberPuzzles": get_num_puzzles(outcome), 
            "qd-score": qd_score(outcome), 
            "children": [] 
        }
    evolveInstances.insert_one(data) 

    evolveInstances.find_one_and_update({"fileId": file_id}, {"$push": {"children": new_file_id}})

    evolveSessions.find_one_and_update({"_id": ObjectId(sessionId)}, {"$set":{"lastId": new_file_id}})

    return {"id": new_file_id, "output": outcome_to_json(outcome, algo.problem_space), "sessionId": sessionId}   

def get_evolve_session(key, sessionId):
    sess = evolveSessions.find_one({"key": key, "_id": ObjectId(sessionId)})
    
    if sess is None:
        print(key, sessionId)
        return None
    
    sess["_id"] = str(sess["_id"])
    return sess 

def get_liked(key, sessionId):
    session = evolveSessions.find_one({"key":key, "_id": ObjectId(sessionId)})

    if session is None:
        
        return None 
    else:
        return session["likedInds"]

def like_ind(key, sessionId, puzzle):
    sess = evolveSessions.find_one({"key": key, "_id": ObjectId(sessionId)}) 

    nextIdx = sess["nextIdx"]

    puzzle["idx"] = nextIdx
    user = evolveSessions.find_one_and_update({"key": key, "_id": ObjectId(sessionId)}, {"$push": {"likedInds": puzzle}, "$inc": {"nextIdx": 1} })
    return puzzle["idx"]

def remove_ind(key, evolveId, puzzleIdx):

    result = sessions.find_one_and_update(
        {"key": key, "_id": ObjectId(evolveId)}, {"$pull": {"likedInds": {"idx": puzzleIdx}}}
    )

    return not result is None

def update_ind(key, evolveId, puzzleIdx, new_ind):

    result = sessions.find_one_and_update(
        {"key": key, "_id": ObjectId(evolveId), "likedInds": {"$elemMatch":{"idx": puzzleIdx}}}, 
        {"$set": {"likedInds.$": new_ind}} 
    )

    return not result is None


def new_session(key, start_time):
    user = get_user(key)
    if not user is None:
        session_template = {
            "key": key, 
            "startTime": start_time,
            "endTime": start_time, 
            "clicks": [],
            "totalTime": 0,
        }
        i = sessions.insert_one(session_template)

        return str(i.inserted_id)
    else:
        return None

def add_click(key, id, data):
    click_data = {"name": data["name"], "rel_time": data["rel_time"], "abs_time": data["abs_time"]}
    if "data" in data:
        click_data["data"] = data["data"]

  
    sessions.find_one_and_update(
        {"key": key, "_id": ObjectId(id)},
        {
            "$push": {"clicks": click_data},
            "$set": {"totalTime": data["rel_time"], "endTime": data["abs_time"]},
        },
    )

def get_examples(space):
    if space == "logic_puzzles":
        return LogicPuzzleSpace().get_examples()