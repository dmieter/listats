import listatsquery as ls
import numpy as np
import pandas as pd

# %% PANEL EXAMPLE


import param
import panel as pn
from panel.theme import Bootstrap, Material, Native, Fast 
from bokeh.models.widgets import HTMLTemplateFormatter, NumberFormatter



#pn.extension(sizing_mode="stretch_width")
pn.extension(design='native')
pn.extension('tabulator', css_files=[pn.io.resources.CSS_URLS['font-awesome']])

tTypes = ls.DF_TOURNAMENTS.type.unique()
tTypes = np.append(tTypes, ['Все'])
tTypes = tTypes[tTypes != None]

indicators = ['Набранные очки', 'Темп', 'Игры', 'Берсерк', 'Перф', 'Место']
indicatorsMap = {'Набранные очки':'score', 'Темп':'avScore', 'Игры':'games', 'Берсерк':'avBerserk', 'Перф':'performance', 'Место':'place'}
indicatorsOpt = {'Набранные очки':False, 'Темп':False, 'Игры':False, 'Берсерк':False, 'Перф':False, 'Место':True}

# %% STYLES

box_style = {'background-color': '#FFFFFF','border-radius': '5px','padding': '10px','box-shadow': '5px 5px 5px #bcbcbc'}
box_empty_style = {'padding': '15px'}
font_style = {'font-family': 'Roboto'}
background_style = {'background': '#edebe9 linear-gradient(to bottom, hsl(37, 12%, 84%), hsl(37, 10%, 92%) 116px) no-repeat'}

img_torpedo_logo = '<img src="https://sun9-42.userapi.com/impg/gVBQcIoT3xffab0mzp4nJ2LQdkPa9pD2z6WlHA/UXDLG7-jK54.jpg?size=501x482&quality=95&sign=be3953ae84447d6a9d10486995f773e0&type=album" height="150">'
img_first_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-massive.svg" height="20">'
img_second_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-silver-1.svg" height="20">'
img_third_place = '<img src="https://lichess1.org/assets/_BM89IP/images/trophy/lichess-bronze-2.svg" height="20">'

stylesheet_tabulator = """

.tabulator {
  padding: 10px;
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
"""

stylesheet_tabulator_small = """

.tabulator {
  padding: 10px;
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
"""


# %% Data preparation


def getRecentTournamentsTab(type):
    if(type == 'Все'):
        type = None
    
    df = ls.getRecentTournaments(type, None, None, 12)    

    df.teamPlace = pd.to_numeric(df.teamPlace)
    df.loc[df.teamPlace == 1, 'teamPlace'] = img_first_place
    df.loc[df.teamPlace == 2, 'teamPlace'] = img_second_place
    df.loc[df.teamPlace == 3, 'teamPlace'] = img_third_place
    
    df['date'] = df['date'].astype(str)
    df['date'] = df['date'].str[:-15]

    df.rename(columns={'eventName': 'Турнир', 
                            'date': 'Дата', 
                            'teamPlace': 'Место', 
                            'teamScore': 'Очки', 
                            'cntPlayers': 'Участники', 
                            'avPerformance': 'Перф', 
                            'avBerserk': 'Берсерк'},
                            inplace = True)                   

    tab_formatters = {
      'Турнир': HTMLTemplateFormatter(template = '<%= value %>'),
      'Место': HTMLTemplateFormatter(template = '<%= value %>')
    }

    tournamentsTab = pn.widgets.Tabulator(
        df[['Турнир', 'Место', 'Дата']],
        layout='fit_data_fill',
        disabled = True, 
        #theme='semantic-ui', 
        show_index = False,
        stylesheets=[stylesheet_tabulator_small],
        formatters=tab_formatters
    )

    return tournamentsTab, df

def prepare_prizes_row(row):
    prizes_row = ''
    if(row['1 место'] > 0):
        prizes_row += str(row['1 место']) + ' x ' + img_first_place + ' '
    if(row['2 место'] > 0):
        prizes_row += str(row['2 место']) + ' x ' + img_second_place + ' '
    if(row['3 место'] > 0):
        prizes_row += str(row['3 место']) + ' x ' + img_third_place + ' '    

    return prizes_row

def getPrizesTab(type):
    if(type == 'Все'):
        type = None
    df = ls.getPodiumsSimple(type, None, None)    

    df['Призы'] = df.apply(lambda x: prepare_prizes_row(x), axis=1)

    tab_formatters = {
      'Призы': HTMLTemplateFormatter(template = '<%= value %>')
    }

    return pn.widgets.Tabulator(
        df[['Игрок', 'Призы', 'Перф']],
        widths={'Призы': 180},
        layout='fit_data',
        show_index = False,
        disabled = True,
        height = 490,
        stylesheets=[stylesheet_tabulator],
        formatters=tab_formatters
    )

def getIndicatorsTab(indicatorDisplay, type):
    indicator = indicatorsMap[indicatorDisplay]
    minimize = indicatorsOpt[indicatorDisplay]
    if(type == 'Все'):
        type = None
    df = ls.calcBestSimpleIndicator(indicator, type, None, None, minimize)

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

    indicatorsTab = pn.widgets.Tabulator(
        df[['Игрок', indicatorDisplay, 'Дата']].head(100),
        layout='fit_data',
        show_index = False,
        disabled = True,
        height = 490,
        stylesheets=[stylesheet_tabulator],
        formatters=tab_formatters
    )

    return indicatorsTab, df


def getTotalScoreTab(type):
    if(type == 'Все'):
        type = None
    df = ls.getMostPointsEarnedWithStats(type, None, None, 100)

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

    return pn.widgets.Tabulator(
        df[['Игрок', 'Очки', 'Игры', 'Темп', 'Берсерк']],
        layout='fit_data',
        show_index = False,
        disabled = True,
        height = 490,
        stylesheets=[stylesheet_tabulator],
        formatters = tab_formatters
    )

def getSingleTournamentTab(tournamentId):

    df = ls.getTournamentPlayers(tournamentId).sort_values(by='place', ascending=True)

    df.loc[df.place == 1, 'place'] = img_first_place
    df.loc[df.place == 2, 'place'] = img_second_place
    df.loc[df.place == 3, 'place'] = img_third_place

    df.rename(columns={'playerName': 'Игрок', 
                       'place': 'Место',
                       'games': 'Игры', 
                       'score': 'Очки',
                       'avBerserk': 'Берсерк'},
                            inplace = True)       

    tab_formatters = {
      'Место': HTMLTemplateFormatter(template = '<%= value %>'), 
      'Очки': NumberFormatter(format='0'),
      'Игры': NumberFormatter(format='0'),
      'Берсерк': {'type': 'progress', 'max': 1 , 'color' : '#c0e2c6'}
    }

    return pn.widgets.Tabulator(
        df[['Игрок', 'Место', 'Игры', 'Очки', 'Берсерк']],
        layout='fit_data',
        show_index = False,
        disabled = True,
        height = 360,
        stylesheets=[stylesheet_tabulator_small],
        formatters = tab_formatters
    )

class TabulatorRecentTournaments:
    def __init__(self, tournament_widget):
        self.tournament_widget = tournament_widget

    def getData(self, type):
        self.tabulator_object, self.df = getRecentTournamentsTab(type)
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
    def __init__(self, player_name_widget, tournament_widget, indicatorDisplay):
        self.player_name_widget = player_name_widget
        self.tournament_widget = tournament_widget
        self.indicatorDisplay = indicatorDisplay

    def getData(self, type):
        self.tabulator_object, self.df = getIndicatorsTab(self.indicatorDisplay, type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])
        self.tournament_widget.value = str(self.df.iloc[event.row]["id"])                
   

class TabulatorTotalScore:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget

    def getData(self, type):
        self.tabulator_object = getTotalScoreTab(type)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])     

class TabulatorSingleTournament:
    def __init__(self, player_name_widget):
        self.player_name_widget = player_name_widget

    def getData(self, tournamentId):
        self.tabulator_object = getSingleTournamentTab(tournamentId)
        self.tabulator_object.on_click(self.click)
        return self.tabulator_object

    def click(self, event):
        self.player_name_widget.value = str(self.tabulator_object.value.iloc[event.row]["Игрок"])     


def getTournamentChart(type):
    import plotly.express as px
    import plotly.graph_objs as go

    if(type == 'Все'):
        type = 'Bundesliga'

    t = ls.getFilteredTournaments(type, None, None).sort_values(by='date', ascending = False).head(200)
    t.teamPlace = pd.to_numeric(t.teamPlace)

    t['color'] = '#7d7d7d'
    t.loc[t.teamPlace == 1, 'color'] = '#FFD700'
    t.loc[t.teamPlace == 2, 'color'] = '#D0D0FF'
    t.loc[t.teamPlace == 3, 'color'] = '#CD7F32'
    if(type == 'Bundesliga'):
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

    #fig = px.line(t, x="Дата", y="Место", title=type, text = "Турнир")
    #fig.update_traces(mode="lines+markers", marker=dict(size=5), line=dict(width=2))
    
    yaxis_format = dict(autorange="reversed")
    if(t['Место'].max() <= 15):
        yaxis_format = dict(autorange="reversed", tick0 = 1, dtick = 1)

    fig = go.Figure()
    fig.add_trace(trace)
    fig.update_layout(
        title = type,
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





def getPageTitlePanel():
    html_pane = pn.pane.HTML("""
<h1>Торпедо Москва</h1>

<table>
  <tr>
    <td><b>Количество Активных Игроков:</b></td>
    <td>56</th>
  </tr>
</table>
                             
""", styles = box_style | font_style)  

    return html_pane

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



# %% SERVER

def get_page_user():
    
    DF_TOURNAMENTS, DF_PLAYERS = ls.loadPandasData()  

    select_type_widget = pn.widgets.Select(options=tTypes.tolist(),value='Все')
    select_indicator_widget = pn.widgets.Select(options=indicators,value='Перф')
    name_input_widget = pn.widgets.TextInput(name='Name Input', value='dmieter')
    tournament_input_widget = pn.widgets.TextInput(name='Tournament Id', value='Eun61pAl')
    
    player_html_pane = pn.bind(getPlayerInfoPanel, name=name_input_widget)
    tournament_html_pane = pn.bind(getTournamentInfoPanel, id=tournament_input_widget)

    tabulatorPrizes = TabulatorPlayerPodiums(name_input_widget)
    bound_prizes_tab = pn.bind(tabulatorPrizes.getData, type=select_type_widget)
    
    tabulatorTournaments = TabulatorRecentTournaments(tournament_input_widget)
    bound_tournamemts_tab = pn.bind(tabulatorTournaments.getData, type=select_type_widget)

    tabulatorPerformance = TabulatorIndicators(name_input_widget, tournament_input_widget, 'Перф')
    bound_performance_tab = pn.bind(tabulatorPerformance.getData, type=select_type_widget)

    tabulatorAverageScore = TabulatorIndicators(name_input_widget, tournament_input_widget, 'Темп')
    bound_avscore_tab = pn.bind(tabulatorAverageScore.getData, type=select_type_widget)

    tabulatorTotalScore = TabulatorTotalScore(name_input_widget)
    bound_totalscore_tab = pn.bind(tabulatorTotalScore.getData, type=select_type_widget)

    tabulatorSingleTournament = TabulatorSingleTournament(name_input_widget)
    bound_singletournament_tab = pn.bind(tabulatorSingleTournament.getData, tournamentId=tournament_input_widget)

    bound_tournaments_chart = pn.bind(getTournamentChart, type=select_type_widget)

    gspec = pn.GridSpec(ncols=8, nrows=30, sizing_mode = "scale_width", styles = background_style)
    #gspec[0, :3] = pn.Row(getPageTitlePanel(), styles = box_style)
    gspec[0, :3] = pn.Row(pn.Column(getTitlePanel('Недавние Турниры'), pn.Column(select_type_widget, bound_tournamemts_tab, styles = box_style), styles = box_empty_style), pn.Column(tournament_html_pane, bound_singletournament_tab, styles = box_style), bound_tournaments_chart)
    gspec[1, :8] = pn.Column(getTitlePanel('Индивидуальные Показатели'), pn.Row(bound_prizes_tab, bound_performance_tab, bound_avscore_tab, bound_totalscore_tab, styles = box_empty_style))
    #gspec[2, :8] = 
    #gspec[2:6, :8] = pn.Row(pn.Column(pn.pane.HTML("<h3>Турниры</h3>", styles = font_style), bound_tournamemts_tab), bound_prizes_tab)
    #gspec[6:, :] = pn.Spacer(styles=dict(background='#00FF00'))
    #gspec[1, :4] = player_html_pane
    #gspec[1, 4:8] = tournament_html_pane
    #gspec[2, 0:2] = pn.Row(select_type_widget, max_height=40)
    #gspec[3, :10] = pn.Row(bound_tournamemts_tab, bound_prizes_tab)
    #gspec[4, :10] = pn.Row(select_indicator_widget, bound_indicators_tab)

    return gspec




pn.serve(get_page_user, port=5003)

# %%
