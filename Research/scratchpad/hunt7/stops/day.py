import sys, json; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops')
import combo_f as M
from engine2 import prepare
sym, day = sys.argv[1], sys.argv[2]; inp = {'slopeCross':True,'minOpenBars':0,'cooldownBars':1,'dayStopR':0,'tightOut':True,'erMin':0.2,'impBody':50}
if len(sys.argv) > 3: inp.update(json.loads(sys.argv[3]))
P=prepare(sym); T=P['T']; tr=M.run(sym, inp); I=M.IMPS[sym]
print('impulses', [(T[i][11:], v[0]) for i,v in sorted(I.items()) if T[i].startswith(day)])
for t in tr:
  if T[t['fill']].startswith(day):
    F=t['feat']; print(T[t['arm']][11:], T[t['fill']][11:], 'L' if t['dir']>0 else 'S', round(t['entry'],3), round(t['stop'],3), T[t['exit']][5:] if t['exit'] else None, t['res'], 'TIGHT' if t['tight'] else '', 'prevNet', F['prevNet'], 'bull/bear', F['bullN'], F['bearN'], 'stopA %.2f' % (t['dir']*(t['entry']-t['stop'])/F['A']), 'candleExtA %.2f' % ((t['entry']-F['L'])/F['A'] if t['dir']>0 else (F['H']-t['entry'])/F['A']))
