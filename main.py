from flask import Flask, render_template, request, url_for, jsonify
from flask_cors import CORS, cross_origin 
app = Flask(__name__)
import database 

@app.route("/add_user", methods=["POST"])
@cross_origin()
def add_account():

    request_data = request.get_json() 

    key = request_data["user"]
    time = request_data["time"]

    result = database.create_user(key, time)

    if not result is None and result != -1:
        response = jsonify("success")
        return response
    elif result is None:
        response = jsonify("existing user")
        return response
    else:
        response = jsonify("something else went wrong")
        return response, 401

@app.route("/new_session", methods=["POST"])
@cross_origin()
def new_session():

    request_data = request.get_json()

    privateKey = request_data["user"]

    result = database.new_session(privateKey, request_data["startTime"])

    if not result is None and result != -1:
        return result
    elif result is None:
        response = jsonify("user does not exist")
        return response, 401

@app.route("/add_click", methods=["POST"])
@cross_origin()
def add_click():

    request_data = request.get_json()


    database.add_click(request_data["user"], request_data["sessionId"], request_data)

    return "success"



@app.route("/like_puzzle", methods=["POST"])
@cross_origin()
def like_puzzle():

    request_data = request.get_json()

    username = request_data["user"]

    result = database.like_ind(username, request_data["evolveId"], request_data["ind"])

    if not result is None:
        return {"idx": result}

    else:
        response = jsonify("user not found")
        return response, 406

@app.route("/remove_puzzle", methods=["POST"])
@cross_origin()
def remove_puzzle():

    request_data = request.get_json()

    username = request_data["user"]

    result = database.remove_ind(username,request_data["evolveId"], request_data["idx"])

    if not result is None:
        return "success"

    else:
        response = jsonify("user not found")
        return response, 406

@app.route("/update_puzzle", methods=["POST"])
@cross_origin()
def update_puzzle():

    request_data = request.get_json()

    username = request_data["user"]

    result = database.update_ind(username,request_data["evolveId"], request_data["idx"], request_data["ind"])

    if not result is None:
        return "success"

    else:
        response = jsonify("user not found")
        return response, 406
     
@app.route("/get_liked_puzzles", methods=["GET"])
@cross_origin()
def get_liked_puzzles():
    username = request.args.get("user")
    session = request.args.get("evolveId")

    result = database.get_liked(username, session)

    if not result is None:
        return jsonify(result)

    else:
        response = jsonify("user not found")
        return response, 406


@app.route("/createScenario", methods=["POST"])
@cross_origin()
def createScenario():
    request_data = request.get_json() 

    results = database.create_scenario(request_data["user"], request_data["time"], request_data["data"])

    return jsonify(results)

@app.route("/updateScenario", methods=["POST"])
@cross_origin()
def updateScenario():
    request_data = request.get_json() 

    results = database.update_scenario_data(request_data["user"], request_data["scenario"], request_data["time"], request_data["data"])

    return jsonify(results)

@app.route("/getScenarios", methods=["GET"])
@cross_origin()
def get_scenarios():
    username = request.args.get("user")
    
    return jsonify(database.get_scenarios(username))

@app.route("/getEvolveSession", methods=["GET"])
@cross_origin()
def get_evolve_session():
    username = request.args.get("user")
    evolve =request.args.get("evolveId")
    
    return jsonify(database.get_evolve_session(username, evolve))


@app.route("/startEvolution", methods=["POST"])
@cross_origin()
def start_evolution():
    request_data = request.get_json()

    result = database.create_evolve_start(request_data["user"], request_data["time"], request_data["cons"], request_data["scenario"]) 

    return jsonify(result)

@app.route("/continueEvolution", methods=["POST"])
@cross_origin()
def continue_evolution():
    request_data = request.get_json()

    result = database.continue_evolution(request_data["user"], request_data["time"], request_data["cons"], request_data["id"])

    if result is None:
        response = jsonify("user not found")
        return response, 406
    else:
        return jsonify(result)


if __name__ == "__main__":
    app.run(port=3000)
