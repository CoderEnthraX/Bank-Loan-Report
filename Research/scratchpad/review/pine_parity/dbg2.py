import sys; sys.path.insert(0,'.')
import emu
import ref
from ref import eprep
P=eprep('MCX_NATURALGAS'); print('mt',P['mt']); R=P['rows']
x=ref.run('MCX_NATURALGAS',dict(mv1On=True, mv1R=0.0, mv2On=True, mv2R=0.6, mv3On=True, mv3R=1.0))[26]
print(repr(x['entry']), repr(R[1070]['l']), R[1070]['l'] <= x['entry'], R[1070]['l']<=x['entry']+0.0)
lim=x['entry']; risk=lim-x['stop']; print(repr(lim+0.0*risk), repr(lim+0.6*risk))
