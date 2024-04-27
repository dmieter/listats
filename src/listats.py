# %% IMPORTS

from urllib.request import Request, urlopen
import numpy as np
import pandas as pd

import json
from bs4 import BeautifulSoup as bs
import time

import datetime
from datetime import timedelta, date

import sys

# %% GLOBALS

import listatsinput as lsi
TEAM_ID, TEAM_NAME, dfPlayersFileName, dfTournamentsFileName = lsi.loadInputTeam()


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

DF_TOURNAMENTS = loadTournamentsDataframe()
DF_PLAYERS = loadPlayersDataframe()

# %% NULLIFY

# Use with care!
#DF_TOURNAMENTS = pd.DataFrame()
#DF_PLAYERS = pd.DataFrame()



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
    try:
        req = Request('https://lichess.org/tournament/'+trId+'/teams')
        response = urlopen(req).read()
    
        place = 9999
        score = 0
        isIndividual = False
    
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

    except BaseException as exception:
        print('Can\'t get team place and score for {}: {}, is it individual arena?'.format(trId, type(exception).__name__)) 
        place = 0
        score = 0
        isIndividual = True    
        
    return place, score, isIndividual

#deprecated
def loadTeamJson(trId, teamId):
    data = loadJson('https://lichess.org/tournament/' + trId + '/team/' + teamId)
    return data

def loadTournamentPlayers(trId):
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
  
#DEPRECATED
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
#print(loaAlldTournamentsList('ecosystem_all_tournaments_20230309'))
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

    players = loadTournamentPlayers(tournamentId)
    
    teamPlayersSummary = []
    for player in players:
        if((isIndividual and 'team' not in player) or player['team'] == teamId):
            playerSummary = getPlayerSummary(player['username'], tournamentId)
            if len(playerSummary) > 0:
                teamPlayersSummary.append(playerSummary)
    
    
    if len(teamPlayersSummary) > 0:
        return pd.DataFrame(teamPlayersSummary).set_index(['playerName', 'tournament'])
    else:
        return pd.DataFrame()

def calcFinishTime(tournamentData):
    startTime = pd.to_datetime(tournamentData['startsAt'])

    return startTime + datetime.timedelta(minutes=int(tournamentData['minutes']))

def decodeTimeControl(tournamentData):
    minutes = tournamentData['clock']['limit']/60
    increment = tournamentData['clock']['increment']

    if minutes < 1 and minutes > 0:
        return '{:.1f}+{}'.format(minutes, increment)
    else:
        return '{:.0f}+{}'.format(minutes, increment)

def getTournamentInfo(tournamentId, tournamentType, tournamentSubtype, teamId):
    tournamentData = loadTournamentJson(tournamentId)
    
    place, score, isIndividual = loadTournamentTeamResult(tournamentId, teamId)

    if 'teamBattle' in tournamentData:
        leadersNum = tournamentData['teamBattle']['nbLeaders']
    else:
        leadersNum = 0
    
    tournamentSummary = {'index': tournamentId,
                         'id': tournamentId, 
                         'type': tournamentType, 
                         'subtype': tournamentSubtype, 
                         'eventName': tournamentData['fullName'], 
                         'date':  tournamentData['startsAt'],
                         'finishTime': calcFinishTime(tournamentData),
                         'timeControl': decodeTimeControl(tournamentData),
                         'timeType' : tournamentData['perf']['name'],
                         'leadersNum' : leadersNum,
                         'teamPlace': place,
                         'teamScore': score
                         }
    return pd.DataFrame(tournamentSummary, index=[0]).set_index(['index']), isIndividual


def loadTournamentFull(tournamentId, tournamentType, tournamentSubtype):
    
    global DF_TOURNAMENTS
    global DF_PLAYERS
    global TEAM_ID
    
    newDfTournament, isIndividual = getTournamentInfo(tournamentId, tournamentType, tournamentSubtype, TEAM_ID)
    newDfPlayers = getTournamentPlayers(tournamentId, TEAM_ID, isIndividual)
    
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

def loadTeamTournaments(data_json):        
        
        tournamentsList = []
        for tournamentJson in data_json:
            if not 'secondsToStart' in tournamentJson.keys():
                tournamentsList.append(tournamentJson['id'])
                print(datetime.datetime.fromtimestamp(tournamentJson['startsAt']/1000))

        tournamentNumber = 1
        tournamentsNumber = len(tournamentsList)
        for tournamentId in tournamentsList:
            print('Loading {} ({} from {})'.format(tournamentId, tournamentNumber, tournamentsNumber))
            try:
                loadTournamentFull(tournamentId, None, None)
            except BaseException as exception:
                try:
                    print('RETRY Loading {} ({} from {})'.format(tournamentId, tournamentNumber, tournamentsNumber))
                    loadTournamentFull(tournamentId, None, None) 
                except BaseException as exception:
                    print('FAILED to load {}. Consider manual upload.'.format(tournamentId, tournamentNumber, tournamentsNumber))

            tournamentNumber += 1
            time.sleep(0.5)


def loadTeamTournamentsFromFile(filename):
    file = open(filename)
    list_json = []
    for line in file.readlines():
        list_json.append(json.loads(line))
    
    loadTeamTournaments(list_json)

def loadTeamTournamentsFromUrl(number):
    #https://lichess.org/api/team/xaj9uK9X/arena?max=10000
    data_json = loadJsonList('https://lichess.org/api/team/{}/arena?max={}'.format(TEAM_ID, number))
    loadTeamTournaments(data_json)




# %% UPLOAD TEST   
    


#loadTeamTournamentsFromUrl(31)
#loadTeamTournamentsFromFile('torpedo_tournaments_23_07_24.json')

#DEBUG
#loadTournamentFull('Mlm5kQLv', None, None) #removed?
#loadTournamentFull('Nrhgv49W', None, None)
#loadTournamentFull('TnUnNHLe', None, None)

