# %% MAIN
import listats as ls
import sys
from datetime import date
 
N = int(sys.argv[1])  # number of recent tournaments to load
if N > 100:
    N = 100

if N > 0:
    print('Loading {} tournaments at {}'.format(N, date.today()))    
    ls.loadTeamTournamentsFromUrl(N)