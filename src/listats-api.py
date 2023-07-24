import listatsquery
# %% SERVER ENDPOINTS

from flask import Flask
from flask import request
from flask import Response
app = Flask(__name__)

def initRequestParams(request, defaultMaxSize):
    maxSize = request.args.get('size')
    maxSize = defaultMaxSize if maxSize is None else int(maxSize)
    daysBack = request.args.get('daysback')
    type = request.args.get('type')
    subType = request.args.get('subtype')

    return type, subType, daysBack, maxSize

@app.route('/user/<username>', methods=['GET'])
def index(username):
    return "Hello, %s!" % username

@app.route('/tournaments', methods=['GET'])
def recentTournaments():
    type, subType, daysBack, maxSize = initRequestParams(request, 20)
    return Response(getRecentTournaments(type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')

@app.route('/tournaments/<tournamentId>', methods=['GET'])
def tournamentPlayers(tournamentId):
    return Response(getTournamentPlayers(tournamentId).to_json(orient='records'), mimetype='application/json')

@app.route('/tournaments/performance', methods=['GET'])
def bestPerformance():
    type, subType, daysBack, maxSize = initRequestParams(request, 100)
    return Response(getBestPerformances(type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')

@app.route('/team/points', methods=['GET'])
def mostTotalPoints():
    type, subType, daysBack, maxSize = initRequestParams(request, 100)
    return Response(getMostPointsEarned(type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')

@app.route('/team/games', methods=['GET'])
def mostTotalGames():
    type, subType, daysBack, maxSize = initRequestParams(request, 100)
    return Response(getMostGamesPlayed(type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')

@app.route('/player/<playerName>/performance', methods=['GET'])
def playerPerformance(playerName):
    type, subType, daysBack, maxSize = initRequestParams(request, 10)
    return Response(getBestPlayerPerformance(playerName, type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')

@app.route('/player/<playerName>/averageScore', methods=['GET'])
def playerAverageScore(playerName):
    type, subType, daysBack, maxSize = initRequestParams(request, 10)
    return Response(getBestPlayerAverageScore(playerName, type, subType, daysBack, maxSize).to_json(orient='records'), mimetype='application/json')


#http://127.0.0.1:4567/tournaments?type=Dark+Master&size=5

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002)