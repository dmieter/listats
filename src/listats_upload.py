# %% MAIN
import listats as ls
import listatsinput as lsi
from datetime import datetime
 
N = int(lsi.loadArgument(2, default = 80))  # number of recent tournaments to load
if N > 1000:
    N = 1000

if N > 0:
    print('Loading {} tournaments at {}'.format(N, datetime.now()))    
    ls.loadTeamTournamentsFromUrl(N)