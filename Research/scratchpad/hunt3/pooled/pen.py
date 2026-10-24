import sys, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,'.')
import pf
from engine2 import prepare
from engine import rma
D=json.load(open('feat.json'))
TR={}
rows=[]
for o in D:
    sym=o['sym']; P=prepare(sym); T=P['T']; H,L,C,O=P['H'],P['L'],P['C'],P['O']; A=rma(P['tr'],14)
    if sym not in TR: TR[sym]=pf.run(sym,{"dayStopR":0})
    m=next((m for m in TR[sym] if m['arm']==o['i'] and m['dir']==o['d']),None)
    if m is None: continue
    f=m['fill']; d=m['dir']; lim=m['entry']
    pen=d*(lim-(L[f] if d>0 else H[f]))
    # bars between arm and fill, min distance close stayed above lim
    rows.append((o['lab'],sym,o['t'],f-m['arm'],round(pen/P['mt'],1),round(pen/A[o['i']],3), m['res']))
rows.sort(key=lambda r:(r[0][:5]!='extra',r[5]))
for r in rows[:30]: print(r)
import collections
print(collections.Counter((r[0][:5],r[3]) for r in rows))
