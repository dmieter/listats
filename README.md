# listats

## listats.py 
contains business logic to parse tournament results into TORPEDO_PLAYERS.pkl and TORPEDO_TOURNAMENTS.pkl pandas dataframes

## listats-api.py
contains business logic with api endpoints for TORPEDO_PLAYERS.pkl and TORPEDO_TOURNAMENTS.pkl as well as demo server starting at http://localhost:5001/

just run: python3 listats-api.py


## Implemented Endpoints:
/tournaments
/tournaments/<tournamentId>
/tournaments/performance
/team/points
/team/games
/player/<playerName>/performance
/player/<playerName>/averageScore

All endpoints above accept the following optional urlencoded parameters:
- type - type of tournaments, for example 'Bundesliga'
- subtype - subtype of tournaments, for example 'Div 2'
- daysback - number of days back to gather info
- size - max size of response

Example: 
GET http://localhost:5001/tournaments?type=Dark+Master&size=5
