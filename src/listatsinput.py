# %% IMPORTS

import sys

# %% GLOBALS

TORPEDO_TEAM_ID = 'xaj9uK9X'
TORPEDO_TEAM_NAME = 'TORPEDO'

ECOSYSTEM_TEAM_ID = 'ChfzrMPn'
ECOSYSTEM_TEAM_NAME = 'ECOSYSTEM'

#TEAM_ID = TORPEDO_TEAM_ID
#dfPlayersFileName = 'TORPEDO_PLAYERS.pkl'
#dfTournamentsFileName = 'TORPEDO_TOURNAMENTS.pkl'
#dfPlayersFileName = 'ECOSYSTEM_PLAYERS.pkl'
#dfTournamentsFileName = 'ECOSYSTEM_TOURNAMENTS.pkl'

def setTorpedoBaseTeam():
    print('Setting TORPEDO as a base team')
    return TORPEDO_TEAM_ID, TORPEDO_TEAM_NAME, 'TORPEDO_PLAYERS.pkl', 'TORPEDO_TOURNAMENTS.pkl'

def setEcosystemBaseTeam():
    print('Setting ECOSYSTEM as a base team')
    return ECOSYSTEM_TEAM_ID, ECOSYSTEM_TEAM_NAME, 'ECOSYSTEM_PLAYERS.pkl', 'ECOSYSTEM_TOURNAMENTS.pkl'

def loadArgument(number, default):
    if len(sys.argv) > number:
        return sys.argv[number]
    else:
        return default

def loadInputTeam():
    input_team = loadArgument(1, TORPEDO_TEAM_NAME)
    if TORPEDO_TEAM_NAME.lower() == input_team.lower():
        return setTorpedoBaseTeam()    
    elif ECOSYSTEM_TEAM_NAME.lower() == input_team.lower():
        return setEcosystemBaseTeam()
    else:
        return setTorpedoBaseTeam()    
    
