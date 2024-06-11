import listatsquery as ls
import listatsinput as lsi
import numpy as np
import pandas as pd

# %% PANEL EXAMPLE


from datetime import datetime
import panel as pn
from panel.theme import Bootstrap, Material, Native, Fast 
from bokeh.models.widgets import HTMLTemplateFormatter, NumberFormatter



#pn.extension(sizing_mode="stretch_width")
pn.extension(design='native')
pn.extension('tabulator', css_files=[pn.io.resources.CSS_URLS['font-awesome']])

js_files = {'listats': 'https://cdn.jsdelivr.net/gh/dmieter/listats/src/js/listats-ui.js'}
pn.extension(js_files=js_files)

tTypes = ls.DF_TOURNAMENTS.type.unique()
SHOW_ALL_TOURNAMENTS = 'Все турниры'
tTypes = np.append([SHOW_ALL_TOURNAMENTS], tTypes)
tTypes = tTypes[tTypes != None]

controlTypes = ls.DF_TOURNAMENTS.timeType.dropna().unique()
controlTypes = np.append([SHOW_ALL_TOURNAMENTS], controlTypes)
controlTypes = controlTypes[controlTypes != None]


class playerTournamentTypes:
  PLAYER_TOURNAMENTS_ALL = 'Все'
  PLAYER_TOURNAMENTS_BEST = 'Лучшие'
  PLAYER_TOURNAMENTS_PRIZES = 'Призовые'

indicators = ['Набранные очки', 'Темп', 'Игры', 'Берсерк', 'Перф', 'Место']
indicatorsMap = {'Набранные очки':'score', 'Темп':'avScore', 'Игры':'games', 'Берсерк':'avBerserk', 'Перф':'performance', 'Место':'place'}
indicatorsOpt = {'Набранные очки':False, 'Темп':False, 'Игры':False, 'Берсерк':False, 'Перф':False, 'Место':True}

SHOW_WHOLE_TIME = 'За все время'
timeMap = {'Неделя' : 7, 'Месяц' : 30, 'Год' : 366, SHOW_WHOLE_TIME : None}
timeTypes = list(timeMap.keys())

pageTitleMap = {lsi.TORPEDO_TEAM_ID : 'ШК Торпедо Москва', lsi.ECOSYSTEM_TEAM_ID : 'ШК Экосистема СБ'}

# %% STYLES

box_style = {'background-color': '#FFFFFF','border-radius': '5px','padding': '10px','box-shadow': '5px 5px 5px #bcbcbc'}
box_empty_style = {'padding-top': '15px', 'padding-left': '15px'}
box_empty_style_small = {'padding-top': '5px', 'padding-left': '5px'}
box_empty_style_h = {'padding-left': '15px'}
box_empty_style_v = {'padding-bottom': '25px'}
font_style = {'font-family': 'Roboto'}
background_style = {'background': '#edebe9 linear-gradient(to bottom, hsl(37, 12%, 84%), hsl(37, 10%, 92%) 116px) no-repeat'}

img_torpedo_logo = '<img src="https://sun9-42.userapi.com/impg/gVBQcIoT3xffab0mzp4nJ2LQdkPa9pD2z6WlHA/UXDLG7-jK54.jpg?size=501x482&quality=95&sign=be3953ae84447d6a9d10486995f773e0&type=album" height="150">'
img_first_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-massive.svg" height="20">'
img_second_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-silver-1.svg" height="20">'
img_third_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-bronze-2.svg" height="20">'

stylesheet_root = """ @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,700;1,400&display=swap'); """

stylesheet_tabulator = """

.tabulator {
  padding: 15px;
  box-shadow: 5px 5px 15px #bcbcbc;
  border-radius: 5px;
}

.tabulator-cell {
  font-family: Roboto;
  font-size: 12px;
  height: 28px;

}

.tabulator-col-title {
  font-family: Roboto;
  font-size: 12px;
  height: 20px;
}

#online{
    padding-left: 3px;
    padding-bottom: 1px;
    font-size: 14px;
    color: #629924;
}
"""

stylesheet_tabulator_small = """

.tabulator {
  padding: 3px;
}

.tabulator-cell {
  font-family: Roboto;
  font-size: 12px;
  height: 28px;

}

.tabulator-col-title {
  font-family: Roboto;
  font-size: 12px;
  height: 20px;
}

#online{
    padding-left: 3px;
    padding-bottom: 1px;
    font-size: 14px;
    color: #629924;
}
"""


class UIProperties:
  """A class that stores UI properties."""

  def __init__(self, is_mobile: bool, theme: str):
    """Initializes a UIProperties object.

    Args:
      is_mobile: Whether the UI is for a mobile device.
      theme: The theme of the UI.
    """

    self.is_mobile = is_mobile
    self.theme = theme


# %% Data preparation

# helper function to calculate sortable place tag with img
def prepareSortingTag(value, max_value = 1000000, ascending = True):
   return '<ts class = "{:.8f}"/>'.format(value/max_value)    

def prepare_tournament_name(row, time = datetime.now()):
    if not pd.isna(row.finishTime) and row.finishTime.timestamp() > time.timestamp():
        return '<b>' + row.eventName + ' (Live)</b> <i id="online">&#x25CF;</i>'
    else:
        return row.eventName
    
def prepare_tournament_date(row, time = datetime.now()):
    if not pd.isna(row.finishTime) and row.finishTime.timestamp() > time.timestamp():
        return '<b>' + row.date + '</b> <i id="online">&#x25CF;</i>'
    else:
        return row.date    

def prepare_sorted_place_value(row, field = 'place'):
  
    place = row[field]

    if(place == 1):
        img = img_first_place
    elif(place == 2):
        img = img_second_place
    elif(place == 3):
        img = img_third_place
    else:
        img = '{:.0f}'.format(place) 

    return prepareSortingTag(place) + img
    

def getRecentTournamentsTab(type, existingTabulator):
    if(type == SHOW_ALL_TOURNAMENTS):
        type = None
    
    df = ls.getRecentTournaments(type, None, None, 100)    

    df.teamPlace = pd.to_numeric(df.teamPlace)
    df['teamPlace'] = df.apply(lambda x: prepare_sorted_place_value(x, field = 'teamPlace'), axis=1)

    currentTime = datetime.now()  
    df['eventName'] = df.apply(lambda x: prepare_tournament_name(x, currentTime), axis=1)          
    
    df['date'] = df['date'].astype(str)
    df['date'] = df['date'].str[:-15]
    #df['date'] = df.apply(lambda x: prepare_tournament_date(x, currentTime), axis=1)

    df['timeControl'] = df['timeControl'].fillna('')

    df.rename(columns={'eventName': 'Турнир', 
                            'date': 'Дата', 
                            'timeControl': 'Часы', 
                            'teamPlace': 'Место', 
                            'teamScore': 'Очки', 
                            'cntPlayers': 'Участники', 
                            'avPerformance': 'Перф', 
                            'avBerserk': 'Берсерк'},
                            inplace = True)                   

    tab_formatters = {
      'Турнир': HTMLTemplateFormatter(template = '<%= value %>'),
      'Дата': HTMLTemplateFormatter(template = '<%= value %>'),
      'Место': HTMLTemplateFormatter(template = '<%= value %>')
    }

    if existingTabulator:
        existingTabulator.value = df[['Турнир', 'Место', 'Часы', 'Дата']]
        tournamentsTab = existingTabulator
    else:     
        tournamentsTab = pn.widgets.Tabulator(
          df[['Турнир', 'Место', 'Часы', 'Дата']],
          widths={'Турнир': 280, 'Дата': 80},
          layout='fit_data_fill',
          disabled = True, 
          #theme='semantic-ui', 
          show_index = False,
          height = 476,
          stylesheets=[stylesheet_tabulator_small],
          formatters=tab_formatters
        )

    return tournamentsTab, df

def prepare_prizes_row(row):
    prizes_row = ''
    total_value = 0
    if(row['1 место'] > 0):
        prizes_row += str(row['1 место']) + ' x ' + img_first_place + ' '
        total_value = total_value + 10000*row['1 место']
    if(row['2 место'] > 0):
        prizes_row += str(row['2 место']) + ' x ' + img_second_place + ' '
        total_value = total_value + 100*row['2 место']
    if(row['3 место'] > 0):
        prizes_row += str(row['3 место']) + ' x ' + img_third_place + ' '
        total_value = total_value + row['3 место']

    return prepareSortingTag(total_value) + prizes_row


def getPrizesTab(type, timePeriod, existingTabulator):
    if(type == SHOW_ALL_TOURNAMENTS):
        type = None
  
    df = ls.getPodiumsSimple(type, None, timeMap[timePeriod])    

    df['Призы'] = df.apply(lambda x: prepare_prizes_row(x), axis=1)

    tab_formatters = {
      'Призы': HTMLTemplateFormatter(template = '<%= value %>')
    }

    if existingTabulator:
        existingTabulator.value = df[['Игрок', 'Призы', 'Всего']]
        return existingTabulator
    else:
        return pn.widgets.Tabulator(
          df[['Игрок', 'Призы', 'Всего']],
          widths={'Призы': 180},
          text_align={'Всего': 'left'},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 420,
          stylesheets=[stylesheet_tabulator_small],
          formatters=tab_formatters
        )

def getIndicatorsTab(indicatorDisplay, type, timePeriod, existingTabulator):
    indicator = indicatorsMap[indicatorDisplay]
    minimize = indicatorsOpt[indicatorDisplay]
    if(type == SHOW_ALL_TOURNAMENTS):
        type = None
        
    df = ls.calcBestSimpleIndicator(indicator, type, None, timeMap[timePeriod], minimize)

    df['date'] = df['date'].astype(str)
    df['date'] = df['date'].str[:-15]

    df.rename(columns={'playerName': 'Игрок', 
                       'date': 'Дата',
                        indicator: indicatorDisplay},
                            inplace = True)       

    tab_formatters = {
      'Перф': NumberFormatter(format='0'),
      'Темп': NumberFormatter(format='0.000')
    }

    if indicatorDisplay == 'Перф':
        df = df[df.games >= 5]
    elif indicatorDisplay == 'Темп':
        df = df[df.games >= 10]


    tab_data = df.head(100)
    tab_data['#'] = tab_data.reset_index().index + 1
    tab_data = tab_data[['#','Игрок', indicatorDisplay, 'Дата']]

    if existingTabulator:
        existingTabulator.value = tab_data
        indicatorsTab = existingTabulator
    else:    
        indicatorsTab = pn.widgets.Tabulator(
          tab_data,
          widths={'Игрок': 150},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 420,
          stylesheets=[stylesheet_tabulator_small],
          formatters=tab_formatters
        )

    return indicatorsTab, df


from io import StringIO
from io import BytesIO
def createInternalRatingFile(date_range, control_type):
    if control_type == SHOW_ALL_TOURNAMENTS:
        control_type = None

    df = ls.getInternalRating(date_range[0].date(), date_range[1].date(), control_type).head(150)

    df.rename(columns={'playerName': 'Игрок', 
                            'internalRating': 'Рейтинг', 
                            'avPlace': 'Место', 
                            'avRating': 'Средний', 
                            'tournamentsNum': 'Турниры'},
                            inplace = True) 
    
    #sio = StringIO()
    #df.to_csv(sio)
    #sio.seek(0)
    #return sio

    io_buffer = BytesIO()
    df.to_excel(io_buffer, index=False)
    io_buffer.seek(0)

    return io_buffer
    

def getInternalRatingTab(existingTabulator, start_date, end_date, control_type):
    if control_type == SHOW_ALL_TOURNAMENTS:
        control_type = None

    df = ls.getInternalRating(start_date.date(), end_date.date(), control_type)

    df.rename(columns={'playerName': 'Игрок', 
                            'internalRating': 'Рейтинг', 
                            'avPlace': 'Место', 
                            'avRating': 'Средний', 
                            'tournamentsNum': 'Турниры'},
                            inplace = True)       

    tab_formatters = {
      'Рейтинг': NumberFormatter(format='0'),
      'Турниры': NumberFormatter(format='0'),
      'Место': NumberFormatter(format='0.0'),
      'Средний': NumberFormatter(format='0.0')
    }


    df['#'] = df.reset_index().index + 1
    tab_data = df[['#', 'Игрок', 'Рейтинг', 'Турниры']]

    if existingTabulator:
        existingTabulator.value = df[['#', 'Игрок', 'Рейтинг', 'Турниры']]
        return existingTabulator
    else:     
        return pn.widgets.Tabulator(
          tab_data,
          widths={'Игрок': 150},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 350,
          stylesheets=[stylesheet_tabulator_small],
          formatters=tab_formatters
        )

def getTotalScoreTab(type, timePeriod, existingTabulator):
    if(type == SHOW_ALL_TOURNAMENTS):
        type = None
    df = ls.getMostPointsEarnedWithStats(type, None, timeMap[timePeriod], 100)

    df.rename(columns={'playerName': 'Игрок', 
                       'totalScore': 'Очки', 
                       'totalGames': 'Игры',
                       'avScore': 'Темп',
                       'avBerserk': 'Берсерк'},
                            inplace = True)       

    tab_formatters = {
      'Очки': NumberFormatter(format='0'),
      'Игры': NumberFormatter(format='0'),
      'Темп': NumberFormatter(format='0.00'),
      'Берсерк': {'type': 'progress', 'max': 1, 'color' : '#c0e2c6'}
    }


    df['#'] = df.reset_index().index + 1
    tab_data = df[['#', 'Игрок', 'Очки', 'Игры', 'Темп', 'Берсерк']]

    if existingTabulator:
        existingTabulator.value = tab_data
        return existingTabulator
    else:
        return pn.widgets.Tabulator(
          tab_data,
          widths={'Игрок': 150},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 420,
          stylesheets=[stylesheet_tabulator_small],
          formatters = tab_formatters
        )

def getSingleTournamentTab(tournamentId, existingTabulator):

    df = ls.getTournamentPlayers(tournamentId).sort_values(by='place', ascending=True)

    df.place = pd.to_numeric(df.place)
    df['place'] = df.apply(lambda x: prepare_sorted_place_value(x), axis=1)          

    df.rename(columns={'playerName': 'Игрок', 
                       'place': 'Место',
                       'games': 'Игры', 
                       'score': 'Очки',
                       'performance': 'Перф',
                       'avBerserk': 'Берсерк'},
                            inplace = True)       

    tab_formatters = {
      'Место': HTMLTemplateFormatter(template = '<%= value %>'), 
      'Очки': NumberFormatter(format='0'),
      'Игры': NumberFormatter(format='0'),
      'Берсерк': {'type': 'progress', 'max': 1 , 'color' : '#c0e2c6'}
    }

    if existingTabulator:
        existingTabulator.value = df[['Игрок', 'Место', 'Игры', 'Очки', 'Перф', 'Берсерк']]
        return existingTabulator
    else:
        return pn.widgets.Tabulator(
          df[['Игрок', 'Место', 'Игры', 'Очки', 'Перф', 'Берсерк']],
          widths={'Игрок': 150},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 300,
          stylesheets=[stylesheet_tabulator_small],
          formatters = tab_formatters
        )




def getSinglePlayerTournamentsTab(name, type, timePeriod, tableType, existingTabulator):
    if(type == SHOW_ALL_TOURNAMENTS):
      type = None

    match tableType:
      case playerTournamentTypes.PLAYER_TOURNAMENTS_BEST:
        df = ls.findPlayerBestTournaments(name, type, None, timeMap[timePeriod])

      case playerTournamentTypes.PLAYER_TOURNAMENTS_PRIZES:
        df = ls.findPlayerPrizes(name, type, None, timeMap[timePeriod])

      case playerTournamentTypes.PLAYER_TOURNAMENTS_ALL:
        df = ls.findPlayerAllTournaments(name, type, None, timeMap[timePeriod])

      case _:
        df = ls.findPlayerBestTournaments(name, type, None, timeMap[timePeriod])

    df = df[['place', 'eventName', 'date', 'games', 'score', 'performance', 'id', 'timeControl']]

    df.place = pd.to_numeric(df.place)
    df['place'] = df.apply(lambda x: prepare_sorted_place_value(x), axis=1)          

    df['date'] = df['date'].astype(str)
    df['date'] = df['date'].str[:-15]

    df.rename(columns={'date': 'Дата',
                       'eventName': 'Турнир',
                       'place': 'Место',
                       'games': 'Игры',
                       'score': 'Очки',
                       'performance': 'Перф',
                       'timeControl' : 'Часы'},
                            inplace = True)       

    tab_formatters = {
      'Место': HTMLTemplateFormatter(template = '<%= value %>'),
      'Очки': NumberFormatter(format='0'),
      'Игры': NumberFormatter(format='0'),
      'Перф': NumberFormatter(format='0')
    }

    if existingTabulator:
        existingTabulator.value = df[['Турнир', 'Место', 'Игры', 'Очки', 'Перф', 'Дата', 'Часы']]
        tabulator = existingTabulator
    else:    
        tabulator = pn.widgets.Tabulator(
          df[['Турнир', 'Место', 'Игры', 'Очки', 'Перф', 'Дата', 'Часы']],
          widths={'Турнир': 200},
          layout='fit_data',
          show_index = False,
          disabled = True,
          height = 215,
          stylesheets=[stylesheet_tabulator_small],
          formatters = tab_formatters
        )

    return tabulator, df


class TabulatorRecentTournaments:
    def __init__(self, tournament_widget):
        self.tournament_widget = tournament_widget
        self.tabulator_object = None

    def getData(self, type):
        self.tabulator_object, self.df = getRecentTournamentsTab(type, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.tournament_widget.value = str(self.df.iloc[event.row]["id"])

class TabulatorInternalRating:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget
        self.tabulator_object = None

    def getData(self, date_range, control_type):
        self.tabulator_object = getInternalRatingTab(self.tabulator_object, date_range[0], date_range[1], control_type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])

class TabulatorPlayerPodiums:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget
        self.tabulator_object = None

    def getData(self, type, timePeriod):
        self.tabulator_object = getPrizesTab(type, timePeriod, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])  


class TabulatorIndicators:
    def __init__(self, player_name_widget, tournament_widget, indicatorDisplay):
        self.player_name_widget = player_name_widget
        self.tournament_widget = tournament_widget
        self.indicatorDisplay = indicatorDisplay
        self.tabulator_object = None

    def getData(self, type, timePeriod):
        self.tabulator_object, self.df = getIndicatorsTab(self.indicatorDisplay, type, timePeriod, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])
        self.tournament_widget.value = str(self.df.iloc[event.row]["id"])                
   

class TabulatorTotalScore:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget
        self.tabulator_object = None

    def getData(self, type, timePeriod):
        self.tabulator_object = getTotalScoreTab(type, timePeriod, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])     

class TabulatorSingleTournament:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget
        self.tabulator_object = None

    def getData(self, tournamentId):
        self.tabulator_object = getSingleTournamentTab(tournamentId, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])     

class TabulatorSinglePlayerPrizes:
    def __init__(self, tournament_widget):
        self.tournament_widget = tournament_widget
        self.tabulator_object = None

    def getData(self, name, type, timePeriod, tableType):
        self.tabulator_object, self.df = getSinglePlayerTournamentsTab(name, type, timePeriod, tableType, self.tabulator_object)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.tournament_widget.value = str(self.df.iloc[event.row]["id"])

def getPlayerPieChart(name, timePeriod):
    import plotly.express as px
    p = ls.getFilteredPlayersLower(None, None, timeMap[timePeriod])
    p = p[p['lowerPlayerName'] == name.lower()]
    g = p.groupby(['type'], 
                    as_index = False).agg(typeCount = ('type', 'count')).sort_values(by=['typeCount'], ascending=False)
    
    fig = px.pie(g, values='typeCount', names='type', title='Турниры', width = 530)
    fig.update_layout(font=dict(
          family="Roboto"
        )
    )
    plot = pn.pane.Plotly(fig, styles = box_empty_style)

    return pn.Column(plot)

def getTournamentChart(type, timePeriod):
    import plotly.express as px
    import plotly.graph_objs as go

    title = type
    if(type == SHOW_ALL_TOURNAMENTS):
        type = 'Bundesliga'
        title = 'Bundesliga '  # fix for strange error when Все switches to Bundesliga


    t = ls.getFilteredTournaments(type, None, timeMap[timePeriod]).sort_values(by='date', ascending = False).head(60)
    t = t[t.teamScore > 0]
    t.teamPlace = pd.to_numeric(t.teamPlace)
    
    t['color'] = '#7d7d7d'
    t.loc[t.teamPlace == 1, 'color'] = '#FFD700'
    t.loc[t.teamPlace == 2, 'color'] = '#D0D0FF'
    t.loc[t.teamPlace == 3, 'color'] = '#CD7F32'
    if(type == 'Bundesliga' or type == 'Rapid League'):
        t.loc[t.teamPlace >= 8, 'color'] = '#FF0000'

    t.rename(columns={'date': 'Дата', 
                       'teamPlace': 'Место',
                       'eventName': 'Турнир'},
                            inplace = True)       

    

    trace = go.Scatter(x = t['Дата'], y = t['Место'], text = t['Турнир'], mode="lines+markers",
                        line_color='#7d7d7d',
        marker=dict(
                color=t["color"],
                size=10,
            ))
    
    yaxis_format = dict(autorange="reversed")
    if(t['Место'].max() <= 15):
        yaxis_format = dict(autorange="reversed", tick0 = 1, dtick = 1)

    fig = go.Figure()
    fig.add_trace(trace)
    fig.update_layout(
        title = title,
        template = 'plotly_white',
        plot_bgcolor='rgba(237, 235, 233, 0.3)',
        font=dict(
          family="Roboto",
          size=13
        ),
        yaxis = yaxis_format,
        xaxis = dict(tickformat='%d/%m/%y'),
        margin=dict(l=60, r=20, t=80, b=70),
        autosize=True
      )

    plot = pn.pane.Plotly(fig, styles = box_empty_style)

    
    return pn.Column(plot, sizing_mode='stretch_width')



def getTextPanel(text):
    return pn.pane.HTML('<b>' + text + '</b>', align = 'start', styles = font_style)

def getTitlePanel(title):
    return pn.pane.HTML('<h3>'+ title +'</h3>', align = 'center', styles = font_style)  
  
def getTitlePanelWithLogo(title):
    return pn.pane.HTML("""
<table>
  <tr>
    <td>""" + img_torpedo_logo + """</td>
    <td><h3>"""+ title +"""</h3></td>
  </tr>
</table>
""", styles = font_style)  


def getTournamentInfoPanel(id):

    info = ls.loadTournamentInfoDict(id)

    html_pane = pn.pane.HTML("""
<h2><a href='https://lichess.org/tournament/""" + str(id) + """'>""" + info["name"] + """</a></h2>

<br>

<table>
    <tr>
    <td>Дата:</td>
    <td>""" + str(info["date"])[:-9] + """</td>
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

""", styles = font_style)

    return html_pane   


stylesheet_player_info = """

table {
	border-collapse: collapse;
}

td {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 10px;
  padding-right: 10px;
}

.basetd {
  padding-top: 0px;
  padding-bottom: 0px;
  padding-left: 3px;
  padding-right: 20px;
}
"""

def getPlayerInfoPanel(name, type, timePeriod):

    if(type == SHOW_ALL_TOURNAMENTS):
        type = None

    info = ls.loadPlayerInfoDict(name, type, None, timeMap[timePeriod])
    #print(info)

    html_pane = pn.pane.HTML("""
<h2><a href='https://lichess.org/@/""" + name + """'>""" + name + """</a></h2>
Активен: """ + str(info["lastActive"])[:-15]  + """
<br><br>
<table>
  <tr>
    <td class = "basetd">
      <table>
          <tr>
            <td class = "basetd">Игр:</td>
            <td>""" + str(info["totalGames"]) + """</td>
          </tr>
          <tr>
            <td class = "basetd">Очков набрано:</td>
            <td>""" + str(info["totalPoints"]) + """</td>
          </tr>
          <tr>
            <td class = "basetd">Берсерк:</td>
            <td>""" + str(info["berserk"]) + """</td>
          </tr>
      </table>
     </td>
     <td>
        <table>
              <td></td>
              <td>Avg</td>
              <td>Max</td>
            </tr>
            <tr>
              <td>Перф:</td>
              <td>""" + str(info["avPerf"]) + """</td>
              <td>""" + str(info["maxPerf"]) + """</td>
            </tr>
            <tr>
              <td>Темп:</td>
              <td>""" + str(info["avScore"]) + """</td>
              <td>""" + str(info["maxAvScore"]) + """</td>
            </tr>
        </table>
      </td>
    </tr>
</table>    


""", styles = font_style, stylesheets = [stylesheet_player_info])

    return html_pane    



stylesheet_panel_title = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap');
#header
.title
{
  font-family: Roboto;
  font-size: 21px;
  color: #222222;
  padding-left: 0px;
}
.bk-input
{
width: 20px;
}

"""

# %% SERVER

import sys


def get_page_user(is_mobile = False):
    
    uiProperties = UIProperties(is_mobile, 'default')

    ls.DF_TOURNAMENTS, ls.DF_PLAYERS = ls.loadPandasData()  

    select_type_widget = pn.widgets.Select(options=tTypes.tolist(),value=SHOW_ALL_TOURNAMENTS, width = 250)
    select_controltype_widget = pn.widgets.Select(options=controlTypes.tolist(),value=SHOW_ALL_TOURNAMENTS, width = 130)
    select_time_widget = pn.widgets.Select(options=timeTypes ,value=SHOW_WHOLE_TIME, width = 150)
    daterange_slider_widget = pn.widgets.DateRangeSlider(
        name='Период',
        start=datetime(2023, 5, 1), end = datetime.today(),
        value=(datetime(2024, 5, 1), datetime.today()),
        step=1,
        width = 350
    )
    name_input_widget = pn.widgets.TextInput(value=ls.getRandomPlayer(), width = 200)
    tournament_input_widget = pn.widgets.TextInput(name='Tournament Id', value=ls.getRandomTournament())
    select_player_table_type_widget = pn.widgets.RadioButtonGroup(options=[playerTournamentTypes.PLAYER_TOURNAMENTS_BEST, playerTournamentTypes.PLAYER_TOURNAMENTS_PRIZES, playerTournamentTypes.PLAYER_TOURNAMENTS_ALL], button_type='light', value = playerTournamentTypes.PLAYER_TOURNAMENTS_BEST)
    
    player_html_pane = pn.bind(getPlayerInfoPanel, name=name_input_widget, type=select_type_widget, timePeriod = select_time_widget)
    tournament_html_pane = pn.bind(getTournamentInfoPanel, id=tournament_input_widget)

    tabulatorPrizes = TabulatorPlayerPodiums(name_input_widget)
    bound_prizes_tab = pn.bind(tabulatorPrizes.getData, type=select_type_widget, timePeriod = select_time_widget)
    
    tabulatorInternalRating = TabulatorInternalRating(name_input_widget)
    bound_internal_rating_tab = pn.bind(tabulatorInternalRating.getData, date_range = daterange_slider_widget, control_type = select_controltype_widget)
    internal_rating_download_widget = pn.widgets.FileDownload(callback=pn.bind(createInternalRatingFile, daterange_slider_widget, select_controltype_widget), filename='internal_rating.xlsx', button_type='success', label = 'Скачать Excel')

    tabulatorTournaments = TabulatorRecentTournaments(tournament_input_widget)
    bound_tournamemts_tab = pn.bind(tabulatorTournaments.getData, type=select_type_widget)

    tabulatorPerformance = TabulatorIndicators(name_input_widget, tournament_input_widget, 'Перф')
    bound_performance_tab = pn.bind(tabulatorPerformance.getData, type=select_type_widget, timePeriod = select_time_widget)

    tabulatorAverageScore = TabulatorIndicators(name_input_widget, tournament_input_widget, 'Темп')
    bound_avscore_tab = pn.bind(tabulatorAverageScore.getData, type=select_type_widget, timePeriod = select_time_widget)

    tabulatorTotalScore = TabulatorTotalScore(name_input_widget)
    bound_totalscore_tab = pn.bind(tabulatorTotalScore.getData, type=select_type_widget, timePeriod = select_time_widget)

    tabulatorSingleTournament = TabulatorSingleTournament(name_input_widget)
    bound_singletournament_tab = pn.bind(tabulatorSingleTournament.getData, tournamentId=tournament_input_widget)

    tabulatorSinglePlayerPrizes = TabulatorSinglePlayerPrizes(tournament_input_widget)
    bound_singleprizes_tab = pn.bind(tabulatorSinglePlayerPrizes.getData, name=name_input_widget, type=select_type_widget, timePeriod = select_time_widget, tableType = select_player_table_type_widget)

    bound_tournaments_chart = pn.bind(getTournamentChart, type=select_type_widget, timePeriod = select_time_widget)
    bound_player_pie_chart = pn.bind(getPlayerPieChart, name=name_input_widget, timePeriod = select_time_widget)

    recent_tournaments_widget = pn.Column(pn.Column(getTitlePanel('Недавние Турниры'), bound_tournamemts_tab, styles = box_style), styles = box_empty_style)
    internal_rating_widget = pn.Column(pn.Column(getTitlePanel('Внутренний Рейтинг'), select_controltype_widget ,daterange_slider_widget, bound_internal_rating_tab, internal_rating_download_widget, styles = box_style), styles = box_empty_style)
    tournamnet_widget = pn.Row(
                            pn.Column(tournament_html_pane, bound_singletournament_tab, styles = box_style, height = 514)
                        , styles = box_empty_style_h)
    
    if not is_mobile:
        player_widget = pn.Row(
                          pn.Row(pn.Column(name_input_widget, player_html_pane, select_player_table_type_widget, bound_singleprizes_tab), bound_player_pie_chart, styles = box_style)
                      , styles = box_empty_style_h)
    else:
        player_widget = pn.Row(
                          pn.Row(pn.Column(name_input_widget, player_html_pane, select_player_table_type_widget, bound_singleprizes_tab), styles = box_style)
                      , styles = box_empty_style_h)
    
    prizes_widget = pn.Row(pn.Column(getTitlePanel('Призовые Места'), bound_prizes_tab, styles = box_style), styles = box_empty_style_h)
    perf_widget = pn.Row(pn.Column(getTitlePanel('Топ 100 по Перформансу'), bound_performance_tab, styles = box_style), styles = box_empty_style_h)
    temp_widget = pn.Row(pn.Column(getTitlePanel('Топ 100 по Темпу'), bound_avscore_tab, styles = box_style), styles = box_empty_style_h)
    score_widget = pn.Row(pn.Column(getTitlePanel('Топ 100 по Очкам'), bound_totalscore_tab, styles = box_style), styles = box_empty_style_h)

    if not is_mobile:
      page_layout = pn.GridSpec(ncols=30, nrows=30, sizing_mode = "scale_width", styles = background_style)
      #page_layout[0, :3] = pn.Row(getPageTitlePanel(), styles = box_style)
      page_layout[0, :30] = pn.Row(recent_tournaments_widget, internal_rating_widget, bound_tournaments_chart, styles = box_empty_style_v)
      page_layout[1, :30] = pn.Row(tournamnet_widget, player_widget, styles = box_empty_style_v)
      page_layout[2, :30] = pn.Row(prizes_widget, perf_widget, temp_widget, score_widget, styles = box_empty_style_v)

    else:
        page_layout = pn.Column(
              pn.Row(internal_rating_widget, styles = box_empty_style_v),
              pn.Row(recent_tournaments_widget, styles = box_empty_style_v),
              pn.Row(tournamnet_widget, styles = box_empty_style_v), 
              pn.Row(player_widget, styles = box_empty_style_v), 
              pn.Row(score_widget, styles = box_empty_style_v), 
              pn.Row(prizes_widget, styles = box_empty_style_v), 
              pn.Row(perf_widget, styles = box_empty_style_v), 
              pn.Row(temp_widget, styles = box_empty_style_v)
              , styles = background_style, sizing_mode = "scale_width")

    
    header_row = pn.Row(getTextPanel(''), select_type_widget, select_time_widget)
    if not is_mobile:
      header_row[0].sizing_mode = 'stretch_width' #stretching first element (empty spacer) to move everything to right

    page = pn.template.BootstrapTemplate(favicon = 'img/favicon.ico', logo = 'img/torpedo_icon.jpg',
    header=header_row, busy_indicator = None, title = pageTitleMap[ls.TEAM_ID], header_background = '#ffffff')
    page.config.raw_css.append(stylesheet_panel_title)
    page.main.append(page_layout)
    return page


def get_mobile_page_user():
    return get_page_user(is_mobile = True)

serve_port = int(lsi.loadArgument(2, default = 5003))
#pn.serve({serve_adress.get(ls.TEAM_NAME, ls.TEAM_NAME) : get_page_user}, port=serve_port, title = pageTitleMap[ls.TEAM_ID], websocket_origin = '*')
pn.serve({ls.TEAM_NAME : get_page_user, 'mobile' : get_mobile_page_user,'' : get_page_user}, port=serve_port, title = pageTitleMap[ls.TEAM_ID], websocket_origin = '*')

# %%
