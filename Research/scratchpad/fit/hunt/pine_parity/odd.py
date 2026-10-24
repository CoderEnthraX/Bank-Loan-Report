import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
norm = {'GC':'03:30','EURUSD':'03:30','NASDAQ':'04:30','US30':'03:30','CRUDE':'09:00','ETH':'05:30','NIFTY':'09:15','SENSEX':'09:15'}
for s in norm:
    P = prepare(s); T=P['T']
    for i in range(1,len(T)):
        if P['daystart'][i] and T[i][11:] != norm[s]:
            print(s, 'odd daystart', T[i], 'prev bar', T[i-1], [ (T[j], round(P['V'][j],4), round((P['H'][j]+P['L'][j]+P['C'][j])/3,4)) for j in range(i-2, min(i+2,len(T)))])
    # gaps between bars > 5 min inside a day (not crossing daystart)
