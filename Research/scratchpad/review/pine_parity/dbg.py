import sys; sys.path.insert(0,'.')
import emu, ref
from ref import eprep
for sym,o,k in [('MCX_NATURALGAS',dict(mv1On=True, mv1R=0.0, mv2On=True, mv2R=0.6, mv3On=True, mv3R=1.0),26),('EURUSD',dict(entryMode='market'),12)]:
    a=ref.run(sym,o)[k]; b=emu.emu(sym,o)[k]; print(a); print(b)
    R=eprep(sym)['rows']
    for i in range(a['fill'], max(a['exit'],b['exit'])+1): print(i,R[i]['t'],R[i]['o'],R[i]['h'],R[i]['l'],R[i]['c'])
