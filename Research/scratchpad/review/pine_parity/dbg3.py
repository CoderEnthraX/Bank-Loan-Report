import sys; sys.path.insert(0,'.')
import emu, reftrace
reftrace.TR=(1064,1072); reftrace.run('MCX_NATURALGAS',dict(mv1On=True, mv1R=0.0, mv2On=True, mv2R=0.6, mv3On=True, mv3R=1.0))
