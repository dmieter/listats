# %% IMPORTS

from urllib.request import Request, urlopen
import numpy as np
import pandas as pd

import json
from bs4 import BeautifulSoup as bs
import time

from datetime import timedelta, date
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# %% GLOBALS

TORPEDO_TEAM_ID = 'xaj9uK9X'
ECOSYSTEM_TEAM_ID = 'ChfzrMPn'
#dfPlayersFileName = 'TORPEDO_PLAYERS.pkl'
#dfTournamentsFileName = 'TORPEDO_TOURNAMENTS.pkl'
dfPlayersFileName = 'ECOSYSTEM_PLAYERS.pkl'
dfTournamentsFileName = 'ECOSYSTEM_TOURNAMENTS.pkl'
#dfPlayersFileName = 'TEST.pkl'
#dfTournamentsFileName = 'TEST.pkl'

pointsMap = {True : np.array([1, 0 ,0]), False : np.array([0 , 0, 1]), None : np.array([0, 1, 0])}



def loadPlayersDataframe():
    return pd.read_pickle(dfPlayersFileName)

def savePlayersDataFrame():
    global DF_PLAYERS
    DF_PLAYERS.to_pickle(dfPlayersFileName)
    
def loadTournamentsDataframe():
    return pd.read_pickle(dfTournamentsFileName)

def saveTournamentsDataFrame():
    global DF_TOURNAMENTS
    DF_TOURNAMENTS.to_pickle(dfTournamentsFileName)  

#DF_TOURNAMENTS = loadTournamentsDataframe()
#DF_PLAYERS = loadPlayersDataframe()

# %% NULLIFY

DF_TOURNAMENTS = pd.DataFrame()
DF_PLAYERS = pd.DataFrame()


# %% API FUNCTIONS

def loadJson(url):
    req = Request(url)
    req.add_header('x-requested-with', 'XMLHttpRequest')
    response = urlopen(req).read()

    data_json = json.loads(response)
    return data_json

def loadJsonList(url):
    req = Request(url)
    req.add_header('x-requested-with', 'XMLHttpRequest')
    response = urlopen(req).read().decode('utf-8')

    list_json = []
    for line in response.splitlines():
        list_json.append(json.loads(line))
    return list_json

def loadTournamentJson(trId):
    data = loadJson('https://lichess.org/api/tournament/' + trId)
    return data

def loadTournamentTeamResult(trId, teamId):
    req = Request('https://lichess.org/tournament/'+trId+'/teams')
    response = urlopen(req).read()
    
    place = 9999
    score = 0
    
    soup = bs(response, features='html.parser')
    for row in soup.find_all('tr'):
        #href = row.find('a', href='/tournament/'+trId+'/team/'+teamId)
        href = row.select('a[href*='+teamId+']') # select href containing team id
        if href:
            tdPlace = row.find('td', {'class': 'rank'})
            if tdPlace:
                place = tdPlace.text
                
            tdScore = row.find('td', {'class': 'total'})
            if tdScore:
                score = tdScore.text
                
            break # stop searching
        
    return place, score

def loadTeamJson(trId, teamId):
    data = loadJson('https://lichess.org/tournament/' + trId + '/team/' + teamId)
    return data

def loadIndividualResultsJson(trId):
    data = loadJsonList('https://lichess.org/api/tournament/' + trId + '/results')
    return data

def loadPlayerJson(trId, playerId):
    data = loadJson('https://lichess.org/tournament/' + trId + '/player/' + playerId)
    return data

def titlesToString(titleGames):
    titlesStr = ''
    for key in titleGames:
        resultArr = titleGames[key]
        titlesStr += ' ' + key + ': (' + str(resultArr[0]) + '/' + str(resultArr[1]) + '/' + str(resultArr[2]) + ')'
    
    return titlesStr
  

# To get all tournaments into a file
#https://lichess.org/api/team/xaj9uK9X/arena?max=10000  (TORPEDO)
#https://lichess.org/api/team/ChfzrMPn/arena?max=10000  (ECOSYSTEM)
# + add square brackets around all lines + "," at the end of each lines (make all lines as entries in array)
def loaAlldTournamentsList(filename):
    file = open(filename)
    data_json = json.loads(file.read())

    tournamentsList = []
    for tournamentJson in data_json:
        tournamentsList.append(tournamentJson['id'])

    return tournamentsList;    

#print(loaAlldTournamentsList('all_tournaments_18102022'))
print(loaAlldTournamentsList('ecosystem_all_tournaments_20230309'))
#loadTournamentTeamResult('RIN0XImQ',TORPEDO_TEAM_ID)  

    
# %% BUSINESS LOAD FUNCTIONS    
def getPlayerSummary(playerName, tournamentId):
    #print(playerName)
    playerInfo = loadPlayerJson(tournamentId, playerName.lower())
    
    playerDetails = playerInfo['player']        
    gamesPlayed = playerDetails['nb']['game']
    if gamesPlayed < 1:
        return {}
    
    titledGames = {}
    for game in playerInfo['pairings']:

        if 'title' in game['op']:
            title = game['op']['title']
            win = game['win']
            points = pointsMap[win]
            
            if title in titledGames:
                titledGames[title] += points
            else:
                titledGames[title] = [0, 0, 0] + points
              
            
    playerSummary = {'playerName': playerDetails['name'], 
                     'tournament': tournamentId, 
                     'games' : gamesPlayed,
                     'score' : playerDetails['score'], 
                     'avScore' : playerDetails['score']/gamesPlayed,
                     'berserk' : playerDetails['nb']['berserk'],
                     'avBerserk' : playerDetails['nb']['berserk']/gamesPlayed,
                     'performance' : playerDetails['performance'],
                     'place' : playerDetails['rank']
                     #,'titledGames' : titlesToString(titledGames)

                     }
    
    for key in titledGames:
        resultArr = titledGames[key]
        playerSummary[key+'_w'] = resultArr[0]
        playerSummary[key+'_d'] = resultArr[1]
        playerSummary[key+'_l'] = resultArr[2]        
    
    return playerSummary 


def getTournamentPlayers(tournamentId, teamId, isIndividual = False):

    if not isIndividual:
        players = loadTeamJson(tournamentId, teamId)['topPlayers']
        playerNameField = 'name'
    else:
        players = loadIndividualResultsJson(tournamentId)
        playerNameField = 'username'
    
    teamPlayersSummary = []
    for player in players:
        playerSummary = getPlayerSummary(player[playerNameField], tournamentId)
        if len(playerSummary) > 0:
            teamPlayersSummary.append(playerSummary)
    
    
    if len(teamPlayersSummary) > 0:
        return pd.DataFrame(teamPlayersSummary).set_index(['playerName', 'tournament'])
    else:
        return pd.DataFrame()

def getTournamentInfo(tournamentId, tournamentType, tournamentSubtype, teamId):
    tournamentData = loadTournamentJson(tournamentId)
    
    try:
        place, score = loadTournamentTeamResult(tournamentId, teamId)
        isIndividual = False
    except BaseException as exception:
        print('Can\'t get team place and score for {}: {}, is it individual arena?'.format(tournamentId, type(exception).__name__)) 
        place = 0
        score = 0
        isIndividual = True
    
    tournamentSummary = {'index': tournamentId,
                         'id': tournamentId, 
                         'type': tournamentType, 
                         'subtype': tournamentSubtype, 
                         'eventName': tournamentData['fullName'], 
                         'date':  tournamentData['startsAt'],
                         'teamPlace': place,
                         'teamScore': score
                         }
    return pd.DataFrame(tournamentSummary, index=[0]).set_index(['index']), isIndividual


def loadTournamentFull(tournamentId, tournamentType, tournamentSubtype, teamId):
    
    global DF_TOURNAMENTS
    global DF_PLAYERS
    
    newDfTournament, isIndividual = getTournamentInfo(tournamentId, tournamentType, tournamentSubtype, teamId)
    newDfPlayers = getTournamentPlayers(tournamentId, teamId, isIndividual)
    
    if newDfTournament.size > 0:
        newDfTournament.date = pd.to_datetime(newDfTournament.date)
        #print(newDfTournament.date)
        
        if DF_TOURNAMENTS.size > 0:
            DF_TOURNAMENTS = newDfTournament.combine_first(DF_TOURNAMENTS)
        else:
            DF_TOURNAMENTS = newDfTournament
    
    if newDfPlayers.size > 0:
        if DF_PLAYERS.size > 0:
            DF_PLAYERS = newDfPlayers.combine_first(DF_PLAYERS)
        else:
            DF_PLAYERS = newDfPlayers
            
    savePlayersDataFrame()
    saveTournamentsDataFrame()


def loadTournamentsFromFile(filename, teamId):
        #tournamentsList = loaAlldTournamentsList('all_tournaments_18102022')
        tournamentsList = loaAlldTournamentsList(filename)
        tournamentNumber = 1
        tournamentsNumber = len(tournamentsList)
        for tournamentId in tournamentsList:
            print('Loading {} ({} from {})'.format(tournamentId, tournamentNumber, tournamentsNumber))
            try:
                loadTournamentFull(tournamentId, None, None, teamId)
            except BaseException as exception:
                  print('RETRY Loading {} ({} from {})'.format(tournamentId, tournamentNumber, tournamentsNumber))
                  loadTournamentFull(tournamentId, None, None, teamId)  
            tournamentNumber += 1
            time.sleep(1)



# %% UPLOAD    
    
    #loadTournamentFull('LMoZn2da', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('Z6rQpTr3', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('mM39GlTh', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('hncSAdC3', 'Bundesliga', 'Div1', TORPEDO_TEAM_ID)
    #loadTournamentFull('m9CjPqg6', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('R403flz4', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('Mhl4xoAR', 'Elite SuperBlitz', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('EVtQ1tTq', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('JLEwt0oP', 'Марафон стенка на стенку', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('KejO4m5E', 'Bundesliga', 'Div1', TORPEDO_TEAM_ID)
    #loadTournamentFull('HsqaiEAx', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('cvfOUqlw', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('tPJxb1I1', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('Rmlt1X58', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('XvuDGTzJ', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('az21hHWo', '16ava Marathon', 'Liga A', TORPEDO_TEAM_ID)
    #loadTournamentFull('RIN0XImQ', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('VBFHR361', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('Co4LEYNq', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('Vjf8FsxA', 'Bundesliga', 'Div2', TORPEDO_TEAM_ID)
    #loadTournamentFull('ArTokuAj', 'Final DARK MASTER', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('4HwiQG5T', 'FGMClub Mega', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('GVrqtEkh', 'Elite SuperBlitz', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('F1Oo2gnd', 'Battle dark master', None, TORPEDO_TEAM_ID)
    #loadTournamentFull('09bkHFZf', 'Марафон стенка на стенку', None, TORPEDO_TEAM_ID)
#loadTournamentFull('JezGNM5V', 'Battle dark master', None, TORPEDO_TEAM_ID)
#loadTournamentFull('9onmEUB1', None, None, TORPEDO_TEAM_ID)
#loadTournamentFull('dJh4vViJ', None, None, TORPEDO_TEAM_ID)


loadTournamentsFromFile('ecosystem_all_tournaments_20230309', ECOSYSTEM_TEAM_ID)
    