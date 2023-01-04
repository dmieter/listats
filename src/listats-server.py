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

def getFilteredPlayers(ttype, tsubtype, periodDays):
    t = getFilteredTournaments(ttype, tsubtype, periodDays)
    return getCorrespondingPlayers(t)

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

    t = t[['id', 'eventName', 'date', 'teamPlace', 'teamScore', 'cntPlayers', 'avPerformance', 'avBerserk']]
    t.avPerformance = np.rint(t.avPerformance).astype('int')

    #t = t.set_index('Турнир')

    #print(t.columns)
    return t

print(getRecentTournaments(None, None, None, 10))    



def calcBestSimpleIndicator(indicator, ttype, tsubtype, periodDays, minimize = False):
      
    df = getFilteredPlayers(ttype, tsubtype, periodDays)
    print(df.columns)
    return df.sort_values(by=[indicator], ascending=minimize)


print(getFilteredPlayers(None, None, None).columns)
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
    

def loadTournamentInfoDict(id):
    t = DF_TOURNAMENTS[DF_TOURNAMENTS.id == id].iloc[0]
    info = {}
    info["name"] = t["eventName"]
    info["date"] = t["date"]
    info["place"] = t["teamPlace"]
    info["score"] = t["teamScore"]

    return info    



#print(getPodiums(None, None, None))
#print(getRecentTournaments(None, None, None, 10))  
# %% TEST
print(loadTournamentInfoDict("JLEwt0oP"))
# %% PANEL EXAMPLE


import param
import panel as pn


pn.extension(sizing_mode="stretch_width")
pn.extension('tabulator', css_files=[pn.io.resources.CSS_URLS['font-awesome']])

tTypes = DF_TOURNAMENTS.type.unique()
tTypes = np.append(tTypes, ['Все'])
tTypes = tTypes[tTypes != None]

indicators = ['Набранные очки', 'Темп', 'Игры', 'Берсерк', 'Перф', 'Место']
indicatorsMap = {'Набранные очки':'score', 'Темп':'avScore', 'Игры':'games', 'Берсерк':'avBerserk', 'Перф':'performance', 'Место':'place'}
indicatorsOpt = {'Набранные очки':False, 'Темп':False, 'Игры':False, 'Берсерк':False, 'Перф':False, 'Место':True}




def getPrizesTab(type):
    if(type == 'Все'):
        df = getPodiums(None, None, None)
    else:
        df = getPodiums(type, None, None)    
        
    return pn.widgets.Tabulator(
        df,
        layout='fit_data', 
        theme='simple', 
        disabled = True,
        height=360
    )

        

def getRecentTornamentsTab(type):
    if(type == 'Все'):
        df = getRecentTournaments(None, None, None, 12)
    else:
        df = getRecentTournaments(type, None, None, 12)    

    df.rename(columns={'eventName': 'Турнир', 
                            'date': 'Дата', 
                            'teamPlace': 'Место', 
                            'teamScore': 'Очки', 
                            'cntPlayers': 'Участники', 
                            'avPerformance': 'Перф', 
                            'avBerserk': 'Берсерк'},
                            inplace = True)                   

    tournamentsTab = pn.widgets.Tabulator(
        df[['Турнир', 'Дата', 'Место', 'Участники']],
        layout='fit_data', 
        theme='simple', 
        disabled = True,
        height=360
    )

    return tournamentsTab, df


def getIndicatorsTab(indicatorDisplay, type):
    indicator = indicatorsMap[indicatorDisplay]
    minimize = indicatorsOpt[indicatorDisplay]
    if(type == 'Все'):
        df = calcBestSimpleIndicator(indicator, None, None, None, minimize)
    else:
        df = calcBestSimpleIndicator(indicator, type, None, None, minimize)
        
    return pn.widgets.Tabulator(
        df,
        layout='fit_data', 
        theme='simple', 
        disabled = True,
        height=360
    )

class TabulatorRecentTournaments:
    def __init__(self, tournament_widget):
        self.tournament_widget = tournament_widget

    def getData(self, type):
        self.tabulator_object, self.df = getRecentTornamentsTab(type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.tournament_widget.value = str(self.df.iloc[event.row]["id"])


class TabulatorPlayerPodiums:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget

    def getData(self, type):
        self.tabulator_object = getPrizesTab(type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])  


class TabulatorIndicators:
    def __init__(self, player_name_widget, tournament_widget):
        self.player_name_widget = player_name_widget
        self.tournament_widget = tournament_widget

    def getData(self, indicatorDisplay, type):
        self.tabulator_object = getIndicatorsTab(indicatorDisplay, type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["playerName"])
        self.tournament_widget.value = str(self.tabulator_object.value.iloc[event.row]["id"])                
   

    

def getPageTitlePanel():
    html_pane = pn.pane.HTML("""
<h1>Торпедо Москва</h1>
<h3>5х Победитель Бундеслиги</h3>

<table>
  <tr>
    <td><b>Количество Активных Игроков:</b></td>
    <td>56</th>
  </tr>
</table>
""", style={'background-color': '#F6F6F6', 'border': '2px solid black',
            'border-radius': '5px', 'padding': '10px'})  

    return html_pane


def getPlayerInfoPanel(name):
    html_pane = pn.pane.HTML("""
<h2>""" + name + """</h2>

<br>

<table>
  <tr>
    <td>Игры:</td>
    <td>1035</td>
  </tr>
  <tr>
    <td>Победы:</td>
    <td>673</td> 
  </tr>
</table>

<table>
  <tr>
    <td></td>
    <td>Средний</td>
    <td>Максимальный</td>
  </tr>
  <tr>
    <td>Перформанс:</td>
    <td>2172</td>
    <td>2673</td>
  </tr>
</table>

""", style={'background-color': '#F6F6F6', 'border': '2px solid black',
            'border-radius': '5px', 'padding': '10px'})  

    return html_pane



def getTournamentInfoPanel(id):
    info = loadTournamentInfoDict(id)

    html_pane = pn.pane.HTML("""
<h2><a href='https://lichess.org/tournament/""" + str(id) + """'>""" + info["name"] + """</a></h2>

<br>

<table>
    <tr>
    <td>Дата:</td>
    <td>""" + str(info["date"]) + """</td>
  </tr>
  <tr>
    <td>Место:</td>
    <td>""" + str(info["place"]) + """</td>
  </tr>
  <tr>
    <td>Набрано очков:</td>
    <td>""" + str(info["score"]) + """</td> 
  </tr>
</table>

<table>
  <tr>
    <td></td>
    <td>Средний</td>
    <td>Максимальный</td>
  </tr>
  <tr>
    <td>Перформанс:</td>
    <td>2172</td>
    <td>2673</td>
  </tr>
</table>

""", style={'background-color': '#F6F6F6', 'border': '2px solid black',
            'border-radius': '5px', 'padding': '10px'})  

    return html_pane    

def get_page_user():
    select_type_widget = pn.widgets.Select(options=tTypes.tolist(),value='Все')
    select_indicator_widget = pn.widgets.Select(options=indicators,value='Перф')
    name_input_widget = pn.widgets.TextInput(name='Name Input', value='dmieter')
    tournament_input_widget = pn.widgets.TextInput(name='Tournament Id', value='kcXyKrOG')
    
    player_html_pane = pn.bind(getPlayerInfoPanel, name=name_input_widget)
    tournament_html_pane = pn.bind(getTournamentInfoPanel, id=tournament_input_widget)

    tabulatorPrizes = TabulatorPlayerPodiums(name_input_widget)
    bound_prizes_tab = pn.bind(tabulatorPrizes.getData, type=select_type_widget)
    
    tabulatorTournaments = TabulatorRecentTournaments(tournament_input_widget)
    bound_tournamemts_tab = pn.bind(tabulatorTournaments.getData, type=select_type_widget)

    tabulatorIndicators = TabulatorIndicators(name_input_widget, tournament_input_widget)
    bound_indicators_tab = pn.bind(tabulatorIndicators.getData, indicatorDisplay = select_indicator_widget, type=select_type_widget)

    gspec = pn.GridSpec(ncols=10, nrows=10, sizing_mode='stretch_both')
    gspec[0, :8] = getPageTitlePanel()
    gspec[1, :4] = player_html_pane
    gspec[1, 4:8] = tournament_html_pane
    gspec[2, 0:2] = pn.Row(select_type_widget, max_height=40)
    gspec[3, :10] = pn.Row(bound_tournamemts_tab, bound_prizes_tab)
    gspec[4, :10] = pn.Row(select_indicator_widget, bound_indicators_tab)
    return gspec




pn.serve(get_page_user, port=5001)

# %%
