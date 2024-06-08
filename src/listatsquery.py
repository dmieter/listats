
# %% IMPORTS

from dataclasses import dataclass
import numpy as np
import pandas as pd
import pickle

from datetime import timedelta, date

# %% GLOBALS
import listatsinput as lsi

TEAM_ID, TEAM_NAME, dfPlayersFileName, dfTournamentsFileName = lsi.loadInputTeam()

#dfPlayersFileName = 'TORPEDO_PLAYERS.pkl'
#dfTournamentsFileName = 'TORPEDO_TOURNAMENTS.pkl'
#dfPlayersFileName = 'ECOSYSTEM_PLAYERS.pkl'
#dfTournamentsFileName = 'ECOSYSTEM_TOURNAMENTS.pkl'

def loadPickle(filename):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)
    
def savePickle(filename, object):
    with open(filename, 'wb') as handle:
        pickle.dump(object, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadPlayersDataframe():
    return pd.read_pickle(dfPlayersFileName)
    
def loadTournamentsDataframe():
    return pd.read_pickle(dfTournamentsFileName)


def retrieveType(tName):
    if('Indonesia'.lower() in tName.lower()):
        return 'Indonesia'
    elif('Bundesliga'.lower() in tName.lower() or 'Lichess Liga '.lower() in tName.lower()):
        return 'Bundesliga'
    elif('MGL ОНЛАЙН ШАТРЫН ЛИГ'.lower() in tName.lower()):  
        return 'MGL ШАТРЫН ЛИГ'
    elif('Lichess Mega'.lower() in tName.lower()):  
        return 'Lichess Mega'
    elif('Champions league'.lower() in tName.lower()):  
        return 'Champions league'
    elif('Friendly team fights'.lower() in tName.lower()):  
        return 'Friendly team fights'
    elif('Lunch League'.lower() in tName.lower()):  
        return 'Lunch League'
    elif('LIGA IBERA'.lower() in tName.lower()):  
        return 'LIGA IBERA'
    elif('Battle elite'.lower() in tName.lower()):  
        return 'Battle Elite'
    elif('Liga América'.lower() in tName.lower()):  
        return 'Liga América'
    elif('dark master'.lower() in tName.lower()):  
        return 'Dark Master'
    elif('Rapid League'.lower() in tName.lower()):  
        return 'Rapid League'
    elif('Лига Суперблица'.lower() in tName.lower()):  
        return 'Лига Суперблица'
    elif('TPR'.lower() in tName.lower()):  
        return 'TPR CHAMPIONSHIP'
    elif('Friendly team fight'.lower() in tName.lower()):  
        return 'Friendly Team Fights'
    elif('Chess960 SuperBlitz'.lower() in tName.lower()):  
        return 'Chess960 SuperBlitz'
    elif('Российский Шахматный Марафон'.lower() in tName.lower()):  
        return 'Российский Шахматный Марафон'
    elif('Экосистема'.lower() in tName.lower() or 'Ecosystem'.lower() in tName.lower() or ' ES '.lower() in tName.lower()):  
        return 'Экосистема Arena'
    else:
        np.nan 

def loadPandasData():
    tournaments = loadTournamentsDataframe()
    players = loadPlayersDataframe().reset_index()

    tournaments.type = tournaments.apply(lambda x: retrieveType(x.eventName), axis=1)
    tournaments['eventName'].replace(' Team Battle$', '', regex = True, inplace = True)

    #print(players.head())
    #print(tournaments.head(50))

    return tournaments, players

DF_TOURNAMENTS, DF_PLAYERS = loadPandasData()

# %% HELP FUNCTIONS
from datetime import datetime

def getFilteredTournaments(ttype, tsubtype, periodDays):
    t = DF_TOURNAMENTS
      
    if ttype:
        t = t[t['type'] == ttype]
          
    if tsubtype:
        t = t[t['subtype'] == tsubtype]
          
    if periodDays:
        t = t[t['date'].dt.date > date.today() - timedelta(days=periodDays)]
    
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
    
def getFilteredPlayersLower(ttype, tsubtype, periodDays, titles=False):    
    players = getFilteredPlayers(ttype, tsubtype, periodDays, titles)
    players['lowerPlayerName'] = players.playerName.str.lower()
    return players


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

#print(getRecentTournaments(None, None, 10, 10)) 
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
    p = getFilteredPlayersLower(ttype, tsubtype, periodDays)
    p = p[p['lowerPlayerName'] == playerName.lower()]
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


def calcInternalRatingForRow(row):

    if row.score == 0:
        return 0

    leadersNum = row.leadersNum if row.leadersNum > 0 else 10 # for inner tournaments with 0 leaders we default to 10 leaders
    
    leader_score = min(leadersNum, row.playersNum) - row.innerPlace + 1     # i.e. if we have players < leadersNum then calc based on players num
    if(row.innerPlace <= 3):
        leader_score = leader_score + 3 - row.innerPlace + 1
    if(row.place <= 3):    
        leader_score = leader_score + 3 - row.place + 1

    #print("For player {} with inner place {}, total place {}, leaders {} and players {} score is: {}".format(row.playerName, row.innerPlace, row.place, row.leadersNum, row.playersNum, leader_score))
    if 'Bundesliga'.lower() in row.eventName.lower() or 'Lichess Liga '.lower() in row.eventName.lower():
        leader_score = leader_score * 2

    return leader_score

def getInternalRating(start_date, end_date, time_type):
    t = DF_TOURNAMENTS
    if time_type:
        t = t[t.timeType == time_type]
    #start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    #end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    t = t[(t.date.dt.date >= start_date) & (t.date.dt.date <= end_date)]

    p = getCorrespondingPlayers(t)
    p = removeTitlesInfo(p)

    p = p.sort_values(['id', 'place'])
    g = p.groupby('id')
    p['innerPlace'] = g.cumcount() + 1
    p['playersNum'] = g['id'].transform('count')
    p = p[(p.leadersNum == 0) | (p.leadersNum >= p.innerPlace)]
    if len(p) > 0:
        p['internalRating'] = p.apply(lambda x: calcInternalRatingForRow(x), axis=1)
    else:
        p['internalRating'] = 0
    g = p.groupby(['playerName'], as_index = False).agg(internalRating = ('internalRating','sum'),
                                                        tournamentsNum = ('innerPlace','count'),
                                                        avRating = ('internalRating','mean'),
                                                        avPlace = ('innerPlace','mean'))
    
    g = g.sort_values(by=['internalRating', 'avPlace', 'tournamentsNum'], ascending=[False, False, False])

    return g


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
                                                        place_3 = ('place_3','sum'),
                                                        podiums_cnt = ('place', 'count'))
    
    g.avPerformance = np.rint(g.avPerformance).astype('int')
    g = g.sort_values(by=['place_1', 'place_2', 'place_3', 'avPerformance', 'playerName'], ascending=[False, False, False, False, True])
    g.rename(columns={'playerName': 'Игрок', 
                            'avPerformance': 'Перф', 
                            'place_1': '1 место', 
                            'place_2': '2 место', 
                            'place_3': '3 место',
                            'podiums_cnt': 'Всего'},
                            inplace = True)
    #g = g.set_index('Игрок')

    return g

def getRandomTournament():
    return DF_TOURNAMENTS.sample().id.iloc[0]

def getRandomPlayer():
    return DF_PLAYERS[DF_PLAYERS.games >= 10].sample().playerName.iloc[0]

def loadTournamentInfoDict(id):
    t = DF_TOURNAMENTS[DF_TOURNAMENTS.id == id].iloc[0]
    info = {}
    info["name"] = t["eventName"]
    info["date"] = t["date"]
    info["place"] = t["teamPlace"]
    info["score"] = t["teamScore"]

    return info   

def findPlayerAllTournaments(name, ttype, tsubtype, periodDays):
    t = getFilteredPlayersLower(ttype, tsubtype, periodDays)
    t = t[t.lowerPlayerName == name.lower()].sort_values(by=['date'], ascending=False)
    return t

def findPlayerPrizes(name, ttype, tsubtype, periodDays):
    t = getFilteredPlayersLower(ttype, tsubtype, periodDays)
    t = t[t.lowerPlayerName == name.lower()]
    return t[t.place <= 3].sort_values(by=['date'], ascending=False)

def findPlayerBestTournaments(name, ttype, tsubtype, periodDays):
    t = getFilteredPlayersLower(ttype, tsubtype, periodDays)
    t = t[t.lowerPlayerName == name.lower()]
    
    df_stats = t[t.games >= 5]
    df_perf = df_stats.nlargest(4, 'performance')
    df_score = df_stats.nlargest(4, 'score')
    df_place = df_stats.nsmallest(4, 'place')

    res = pd.concat([df_perf, df_score, df_place]).drop_duplicates().reset_index(drop=True).sort_values(by=['date'], ascending=False)
    return res

def loadPlayerInfoDict(name, ttype, tsubtype, periodDays):
    t = getFilteredPlayersLower(ttype, tsubtype, periodDays)
    t = t[t.lowerPlayerName == name.lower()]
    info = {}
    info["lastActive"] = t.date.max()
    
    maxPerf = t[t.games >=5].performance.max()
    

    avPerf = t[t.games >=5].performance.mean()
    maxAvScore = t[t.games >=10].avScore.max()
    totalGames = t.games.sum()
    totalPoints = t.score.sum()
    avScore = totalPoints/totalGames if totalGames > 0 else pd.NA
    berserk = 100*t.berserk.sum()/totalGames if totalGames > 0 else pd.NA

    info["maxPerf"] = '{:.0f}'.format(maxPerf) if not pd.isna(maxPerf) else '-'
    info["avPerf"] = '{:.0f}'.format(avPerf) if not pd.isna(avPerf) else '-'
    info["maxAvScore"] = '{:.2f}'.format(maxAvScore) if not pd.isna(maxAvScore) else '-'
    info["avScore"] = '{:.2f}'.format(avScore) if not pd.isna(avScore) else '-'
    info["totalGames"] = '{:.0f}'.format(totalGames)
    info["totalPoints"] = '{:.0f}'.format(totalPoints)
    info["berserk"] = '{:.0f}%'.format(berserk) if not pd.isna(berserk) else '-'
   
    return info 

#print(loadPlayerInfoDict('Aqua_Blazing', 'Mega', None, None))
#print(getRecentTournaments(None, None, None, 100)[['date', 'finishTime']])