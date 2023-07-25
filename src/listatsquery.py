
# %% IMPORTS

from dataclasses import dataclass
import numpy as np
import pandas as pd

from datetime import timedelta, date

# %% GLOBALS

dfPlayersFileName = 'TORPEDO_PLAYERS.pkl'
dfTournamentsFileName = 'TORPEDO_TOURNAMENTS.pkl'
#dfPlayersFileName = 'ECOSYSTEM_PLAYERS.pkl'
#dfTournamentsFileName = 'ECOSYSTEM_TOURNAMENTS.pkl'

def loadPlayersDataframe():
    return pd.read_pickle(dfPlayersFileName)
    
def loadTournamentsDataframe():
    return pd.read_pickle(dfTournamentsFileName)


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
    elif('Rapid League'.lower() in tName.lower()):  
        return 'Rapid League'
    elif('TPR'.lower() in tName.lower()):  
        return 'TPR CHAMPIONSHIP'
    elif('Chess960 SuperBlitz'.lower() in tName.lower()):  
        return 'Chess960 SuperBlitz'
    elif('Российский Шахматный Марафон'.lower() in tName.lower()):  
        return 'Российский Шахматный Марафон'
    elif('Экосистема'.lower() in tName.lower() and 'Arena'.lower() in tName.lower()):  
        return 'Экосистема Arena'
    else:
        np.nan 

def loadPandasData():
    tournaments = loadTournamentsDataframe()
    players = loadPlayersDataframe().reset_index()

    tournaments.type = tournaments.apply(lambda x: retrieveType(x.eventName), axis=1)

    #print(players.head())
    #print(tournaments.head(50))

    return tournaments, players

DF_TOURNAMENTS, DF_PLAYERS = loadPandasData()    

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
       'WGM_d', 'WGM_l', 'WGM_w', 'WIM_d', 'WIM_l', 'WIM_w'], errors='ignore')

def getFilteredPlayers(ttype, tsubtype, periodDays, titles=False):
    t = getFilteredTournaments(ttype, tsubtype, periodDays)
    p = getCorrespondingPlayers(t)
    if(titles):
        return p
    else:
        return removeTitlesInfo(p)



def getCorrespondingPlayers(dfTournaments):
    p = DF_PLAYERS.set_index('tournament')
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
    p = DF_PLAYERS
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

def getMostPointsEarnedWithStats(ttype, tsubtype, periodDays, maxNumber):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    
    
    g = p.groupby(['playerName'], as_index = False).agg(totalScore = ('score','sum'), 
                                                        totalGames = ('games','sum'),
                                                        totalBerserk = ('berserk', 'sum'))
    g = g[g['totalGames'] >= 5]
    g['avBerserk'] = g.totalBerserk/g.totalGames
    g['avScore'] = g.totalScore/g.totalGames

    return g.sort_values(by=['totalScore'], ascending=False).head(maxNumber)

    

#getMostPointsEarnedWithStats(None, None, None, 100)

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
#print(getBestPlayerAverageScore('UGotToBeKiddinMe', None, None, None, 20)) 
#print(getMostGamesPlayed(None, None, None, 20)) 
#print(getMostPointsEarned(None, None, None, 20)) 

#print(getFilteredPlayers(None, None, None).columns)
#indicator = 'place'
#r = calcBestSimpleIndicator(indicator, None, None, None, True)
#print(r.head())
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




def getPodiumsSimple(ttype, tsubtype, periodDays):
    p = getFilteredPlayers(ttype, tsubtype, periodDays)
    
    p = p[p['place'] <= 3]
    
    p.fillna('', inplace=True)
    
    p['place_1'] = p.apply(lambda x: 1 if x['place'] == 1 else 0, axis=1)
    p['place_2'] = p.apply(lambda x: 1 if x['place'] == 2 else 0, axis=1)
    p['place_3'] = p.apply(lambda x: 1 if x['place'] == 3 else 0, axis=1)
    
    
    #print(g.columns)
    g = p.groupby(['playerName'], as_index = False).agg(avPerformance = ('performance','mean'),
                                                        place_1 = ('place_1','sum'),
                                                        place_2 = ('place_2','sum'),
                                                        place_3 = ('place_3','sum'))
    

    p['place_3'] = p.apply(lambda x: 1 if x['place'] == 3 else 0, axis=1)
    
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

def getRandomTournament():
    return DF_TOURNAMENTS.sample().id.iloc[0]

def loadTournamentInfoDict(id):
    t = DF_TOURNAMENTS[DF_TOURNAMENTS.id == id].iloc[0]
    info = {}
    info["name"] = t["eventName"]
    info["date"] = t["date"]
    info["place"] = t["teamPlace"]
    info["score"] = t["teamScore"]

    return info   

def getTournamentChart(type):


    t = getFilteredTournaments(type, None, None).sort_values(by='date', ascending = False).head(100)

    #print(t.head())

getTournamentChart(None)
