import json 
import statistics

import matplotlib.pyplot as plt
def get_data(folder, num_users):
    user_data = [] 

    for u in range(num_users):
        file=open("{}/user_{}.json".format(folder, u), "r")
        j = json.load(file)
        file.close()

        user_data.append(j)
    return user_data

def print_times(data):

    times = [j["total_time"] for j in data]

    minutes = [t / 1000 / 60 for t in times]

    print("minutes")
    print(minutes)

    print("\nAvg:{}".format(statistics.mean(minutes)))
    print("\nMed:{}".format(statistics.median(minutes)))
    print("STD:{}".format(statistics.stdev(minutes)))



    sessions = [j["num_sessions"] for j in data]

    print("\n\nSessions")
    print(sessions)

    print("\nAvg:{}".format(statistics.mean((sessions))))
    print("STD:{}".format(statistics.stdev((sessions))))

    e_sessions = [len(j["evolve_sessions"]) for j in data]

    print("\n\nEvolve Sessions")
    print(e_sessions)

    print("\nAvg:{}".format(statistics.mean((e_sessions))))
    print("STD:{}".format(statistics.stdev((e_sessions))))

    e_instances = [len(j["evolve_instances"]) for j in data]

    print("\n\nEvolve Instances")
    print(e_instances)

    print("\nAvg:{}".format(statistics.mean((e_instances))))
    print("STD:{}".format(statistics.stdev((e_instances))))

def get_modes(data):
    modes = {}
    for j in data:
        if not j["mode"] in modes:
            modes[j["mode"]] = [] 
        modes[j["mode"]].append(j)
    return modes

def get_mode_values(modes):
    qd_scores = {} 
    times = {} 
    evolve_ins ={}

    for mode in modes:
        qd_scores[mode] = []
        times[mode] = [] 
        evolve_ins[mode] = [] 
        for user in modes[mode]:
            qd = [i["qd-score"] for i in user["evolve_instances"] if "qd-score" in i and not i["qd-score"] is None ] 
            qd_scores[mode] += qd 

            times[mode].append(user["total_time"] / 1000 / 60)
            evolve_ins[mode].append(len(user["evolve_instances"]))
    
    return {"qd-scores": qd_scores, "times":times, "evolve_ins":evolve_ins}

def print_mode_avgs(mod_avgs):
    for value in mod_avgs:
        print("\n", value)
        for mode in mod_avgs[value]:
            if len(mod_avgs[value][mode]) == 1:
                print("\t{}: mean={}".format(mode, statistics.mean(mod_avgs[value][mode])))
            elif len(mod_avgs[value][mode]) >= 2:
                if value == "times":
                    print(mod_avgs[value][mode])
                    print("\t{}: median={}, std={}".format(mode, statistics.median(mod_avgs[value][mode]),  statistics.stdev(mod_avgs[value][mode]))) 
                else: 
                    print("\t{}: mean={}, std={}".format(mode, statistics.mean(mod_avgs[value][mode]),  statistics.stdev(mod_avgs[value][mode])))
            else:
                print("\t{}: no data".format(mode))

def get_con_stats(user_data):
    all_con_list = []
    first_cons = [] 
    not_first_cons = []
    session_dict = {}
    cons_by_mode = {} 

    for user in user_data: 
        for inst in user["evolve_instances"]:
            if not user["mode"] in cons_by_mode:
                cons_by_mode[user["mode"]] = []
            cons_by_mode[user["mode"]].append(inst["cons"])
            all_con_list.append(inst["cons"])
            if inst["sessionCount"] == 0:
                first_cons.append(inst["cons"])

            else:
                not_first_cons.append(inst["cons"])

            
            if not inst["sessionCount"] in session_dict:
                session_dict[inst["sessionCount"]] = [] 
            session_dict[inst["sessionCount"]].append(inst["cons"])
    
    all_lens = [len(con) for con in all_con_list]
    

    print("\nAll con mean:{}, std:{}".format(statistics.mean(all_lens), statistics.stdev(all_lens)))

    for mode in cons_by_mode:
        mode_lens = [len(con) for con in cons_by_mode[mode]]
        print("\tFor mode {} - mean:{}, std:{}".format(mode, statistics.mean(mode_lens), statistics.stdev(mode_lens)))
    type_counts = {} 
    hint_counts = {} 

    for li in all_con_list:
        for con in li:
            rule = list(con["con"])[0]
            if not rule in hint_counts:
                hint_counts[rule] = 0 
            hint_counts[rule] += 1  
            if not con["origin"] in type_counts:
                type_counts[con["origin"]] = 0 
            type_counts[con["origin"]] += 1 
    print("Origin Counts")
    print(type_counts)

    print("\nHint type counts")
    print(hint_counts)
    

    for key in session_dict:
        lengths = [len(con) for con in session_dict[key]]
        if (len(lengths) > 2):
            print("Session {}: mean:{}, std:{}, count:{}".format(key, statistics.mean(lengths), statistics.stdev(lengths), len(lengths)))
        else:
            print("Session {}: mean:{}, count:{}".format(key, statistics.mean(lengths), len(lengths)))

def update_mode(file_id, evolve_instances, state_dict,  last_cons = []): 
    # find evolve instance 
    instance = [inst for inst in evolve_instances if inst["fileId"] == file_id]

    if len(instance) == 0:
        print("Couldn't find instance")
        return 
    elif len(instance) > 1:
        print("Too many instances")
        return 

    instance = instance[0]
    cons = instance["cons"]

    details = { "delete": 0, "add-random":0, "add-generated":0} 
    for con in last_cons:
        if not con in cons:
            details["delete"] += 1 
     
     
    
    for con in cons:
        if not con in last_cons:
            if con["origin"] == "generated":
                details["add-generated"] += 1 
            else:
                details["add-random"] += 1 
    


    if not len(last_cons) in state_dict:
        state_dict[len(last_cons)] = []
    
    is_repeat = False 
    
    for i, state in enumerate(state_dict[len(last_cons)]):
        if  state["actions"] == details:
            is_repeat = True 
            state_dict[len(last_cons)][i]["count"] += 1 
    
    if not is_repeat:
        state_dict[len(last_cons)].append({ "actions": details, "count": 1})
    
    if len(instance["children"]) > 0:
        for child in instance["children"]:
            update_mode(child, evolve_instances, state_dict,  cons)


def create_player_model(user_data):
    state_dict = {}
    visits = {}
    for user in user_data:
        for s in user["evolve_sessions"]: 
            update_mode(s["startId"], user["evolve_instances"], state_dict) 
        for e in user["evolve_instances"]:
            if not len(e["cons"]) in visits:
                visits[len(e["cons"])] = 0 
            visits[len(e["cons"])] += 1 
    percentage_dict = {}

    for key in state_dict:
        percentage_dict[key] = []
        actions = state_dict[key]
        s = sum([action["count"] for action in actions])

        for action in actions: 
            per = action["count"] / s 
            percentage_dict[key].append((per, action["actions"]))

    print(visits)
    return percentage_dict


if __name__ == "__main__":
    data = get_data("userData", 30)
    print_times(data)

    print(create_player_model(data))

    get_con_stats(data)

    mode_data = get_modes(data)
    print("\n")
    for mode in mode_data:
        print("Mode:{} has {} users".format(mode, len(mode_data[mode])))
    mode_values = get_mode_values(mode_data)
    print_mode_avgs(mode_values)
