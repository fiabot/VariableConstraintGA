import json 
import statistics
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
                print("\t{}: mean={}, std={}".format(mode, statistics.mean(mod_avgs[value][mode]),  statistics.stdev(mod_avgs[value][mode])))
            else:
                print("\t{}: no data".format(mode))

if __name__ == "__main__":
    data = get_data("userData", 2)
    print_times(data)

    mode_data = get_modes(data)
    mode_values = get_mode_values(mode_data)
    print_mode_avgs(mode_values)
