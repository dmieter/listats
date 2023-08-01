# %% MAIN
import listats as ls
import sys
 
N = int(sys.argv[1])  # number of recent tournaments to load
if N > 100:
    N = 100

if N > 0:    
    ls.loadTeamTournamentsFromUrl(N)