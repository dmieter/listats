
# %% IMPORTS

from dataclasses import dataclass
import numpy as np
import pandas as pd

from datetime import timedelta, date

# %% GLOBALS

dfPlayersFileName = 'TORPEDO_PLAYERS.pkl'
dfTournamentsFileName = 'TORPEDO_TOURNAMENTS.pkl'

def loadPlayersDataframe():
    return pd.read_pickle(dfPlayersFileName)
    
def loadTournamentsDataframe():
    return pd.read_pickle(dfTournamentsFileName)

DF_TOURNAMENTS = loadTournamentsDataframe()
DF_PLAYERS = loadPlayersDataframe()

def retrieveType(tName):
    if('Indonesia'.lower() in tName.lower()):
        return 'Indonesia'
    elif('Bundesliga'.lower() in tName.lower()):  
        return 'Bundesliga'
    elif('Mega A'.lower() in tName.lower()):  
        return 'Mega'
    elif('dark master'.lower() in tName.lower()):  
        return 'Dark Master'
    elif('МАРАФОН Стенка'.lower() in tName.lower()):  
        return 'МАРАФОН Стенка'
    elif('FGMClub Mega'.lower() in tName.lower()):  
        return 'FGMClub Mega'
    else:
        np.nan 

DF_TOURNAMENTS.type = DF_TOURNAMENTS.apply(lambda x: retrieveType(x.eventName), axis=1)

# %% HELP FUNCTIONS

def getFilteredTournaments(ttype, tsubtype, periodDays):
    t = DF_TOURNAMENTS
      
    if ttype:
        t = t[t['type'] == ttype]
          
    if tsubtype:
        t = t[t['subtype'] == tsubtype]
          
    if periodDays:
        t = t[t['date'] > date.today() - timedelta(days=periodDays)]
    
    return t

def removeTitlesInfo(p):
    return p.drop(columns=['CM_d', 'CM_l', 'CM_w', 'FM_d', 'FM_l', 'FM_w', 'GM_d',
       'GM_l', 'GM_w', 'IM_d', 'IM_l', 'IM_w', 'LM_d', 'LM_l', 'LM_w', 'NM_d',
       'NM_l', 'NM_w', 'WCM_d', 'WCM_l', 'WCM_w', 'WFM_d', 'WFM_l', 'WFM_w',
       'WGM_d', 'WGM_l', 'WGM_w', 'WIM_d', 'WIM_l', 'WIM_w'])

def getFilteredPlayers(ttype, tsubtype, periodDays, titles=False):
    t = getFilteredTournaments(ttype, tsubtype, periodDays)
    p = getCorrespondingPlayers(t)
    if(titles):
        return p
    else:
        return removeTitlesInfo(p)



def getCorrespondingPlayers(dfTournaments):
    p = DF_PLAYERS.reset_index().set_index('tournament')
    m = dfTournaments.merge(p, left_on = 'id', right_on = 'tournament', how = 'left')    
     
    #print(m.columns)
    return m

# %% BUSINESS FUNCTIONS

def getRecentTournaments(ttype, tsubtype, periodDays, maxNumber):
    # get tornaments to show
    
    t = getFilteredTournaments(ttype, tsubtype, periodDays)
    t.teamScore = t.teamScore.astype('int')
    t = t[t.teamScore > 0]
    t = t.sort_values(by='date', ascending = False).head(maxNumber)
    
    # get aggregate details
    p = getCorrespondingPlayers(t)
    g = p.groupby(['id'], as_index = False).agg(cntPlayers = ('id','count'),
                                                avPerformance = ('performance','mean'),
                                                avBerserk = ('avBerserk','mean'))

    # merge result
    t = pd.merge(t, g, left_on = 'id', right_on = 'id', how = 'left')

    #t = t[['id', 'eventName', 'type', 'subtype', 'date', 'teamPlace', 'teamScore', 'cntPlayers', 'avPerformance', 'avBerserk']]
    t.avPerformance = np.rint(t.avPerformance).astype('int')

    #t = t.set_index('Турнир')

    #print(t.columns)
    return t

#print(getRecentTournaments(None, None, None, 10)) 
#print(getRecentTournaments(None, None, None, 10).columns)    

def getTournamentPlayers(tournamentId):
    p = DF_PLAYERS.reset_index()
    p = p[p['tournament'] == tournamentId]

    return p[['playerName', 'tournament', 'avBerserk', 'avScore', 'berserk', 'games', 'performance', 'place', 'score']]

#print(getTournamentPlayers('hbVklgI1')) 

def calcBestSimpleIndicator(indicator, ttype, tsubtype, periodDays, minimize = False):
    df = getFilteredPlayers(ttype, tsubtype, periodDays)
    return df.sort_values(by=[indicator], ascending=minimize)

def getMostGamesPlayed(ttype, tsubtype, periodDays, maxNumber):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    g = p.groupby(['playerName'], as_index = False).agg(totalGames = ('games','sum'))
    return g.sort_values(by=['totalGames'], ascending=False).head(maxNumber)

def getMostPointsEarned(ttype, tsubtype, periodDays, maxNumber):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    g = p.groupby(['playerName'], as_index = False).agg(totalScore = ('score','sum'))
    return g.sort_values(by=['totalScore'], ascending=False).head(maxNumber)

def getBestPerformances(ttype, tsubtype, periodDays, maxNumber):
    return calcBestSimpleIndicator('performance', ttype, tsubtype, periodDays, False).head(maxNumber)

def getBestPlayerIndicator(playerName, indicator, ttype, tsubtype, periodDays, minimize = False):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    p = p[p['playerName'] == playerName]
    return p.sort_values(by=[indicator], ascending=minimize)

def getBestPlayerPerformance(playerName, ttype, tsubtype, periodDays, maxSize):
    return getBestPlayerIndicator(playerName, 'performance', ttype, tsubtype, periodDays, False).head(maxSize)

def getBestPlayerAverageScore(playerName, ttype, tsubtype, periodDays, maxSize):
    return getBestPlayerIndicator(playerName, 'avScore', ttype, tsubtype, periodDays, False).head(maxSize)


#print(getBestPlayerPerformance('EasyTempo75', None, None, None, 20)) 
print(getBestPlayerAverageScore('UGotToBeKiddinMe', None, None, None, 20)) 
#print(getMostGamesPlayed(None, None, None, 20)) 
#print(getMostPointsEarned(None, None, None, 20)) 

#print(getFilteredPlayers(None, None, None).columns)
#indicator = 'place'
#r = calcBestSimpleIndicator(indicator, None, None, None, True)
#print(r[['playerName', indicator, 'eventName']].head(20))  


def getPlayersRecentParticipations(ttype, tsubtype, periodDays):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    #print(p.head())
    g = p.groupby(['playerName'], 
                    as_index = False).agg(recentTournamnet = ('date', 'max'),
                                            avgPerf = ('performance', 'mean'),
                                            totalGames = ('games', 'sum')
                                            ).sort_values(by=['recentTournamnet', 'playerName'], ascending=False)
    return g

#print(getPlayersRecentParticipations(None, None, None))
#with open(r'participation_report.txt', 'w') as f:
#    f.write(getPlayersRecentParticipations(None, None, None).to_string(header=True, index=False))

 

def getPodiumString(row):
    podiumString = row['type']
    if row['subtype']:
        podiumString += '('+str(row['subtype'])+')'
    
    podiumString += ' ' + str(row['place']) + ' place: ' + str(row['cnt']) + 'x'
    
    if row['cnt'] > 1:
        podiumString += 's'
    
    podiumString += ' (' + row['dates'] + ')<br>' 
    
    return podiumString

def getPodiums(ttype, tsubtype, periodDays):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    p['dateStr'] = pd.to_datetime(p['date']).dt.strftime('%Y-%m-%d')
    
    p = p[p['place'] <= 3]
    
    p.fillna('', inplace=True)
    g = p.groupby(['playerName', 'place', 'type', 'subtype'], as_index = False).agg(cnt = ('playerName','count'),
                                                                 avPerformance = ('performance','mean'),
                                                                 dates = ('dateStr', ', '.join))
    
    #print(g.columns)
    
    g['place_1'] = g.apply(lambda x: x['cnt'] if x['place'] == 1 else 0, axis=1)
    g['place_2'] = g.apply(lambda x: x['cnt'] if x['place'] == 2 else 0, axis=1)
    g['place_3'] = g.apply(lambda x: x['cnt'] if x['place'] == 3 else 0, axis=1)
    
    
    #print(g.columns)
    g = g.groupby(['playerName'], as_index = False).agg(avPerformance = ('avPerformance','mean'),
                                                        place_1 = ('place_1','sum'),
                                                        place_2 = ('place_2','sum'),
                                                        place_3 = ('place_3','sum'))
    
    g.avPerformance = np.rint(g.avPerformance).astype('int')
    g = g.sort_values(by=['place_1', 'place_2', 'place_3', 'avPerformance', 'playerName'], ascending=[False, False, False, False, True])
    g.rename(columns={'playerName': 'Игрок', 
                            'avPerformance': 'Перф', 
                            'place_1': '1 место', 
                            'place_2': '2 место', 
                            'place_3': '3 место'},
                            inplace = True)
    #g = g.set_index('Игрок')

    return g

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
    app.run(host='127.0.0.1', port=4567)