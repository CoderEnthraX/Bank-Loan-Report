import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from volrec import recover
from arp_data import load
import collections
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','ETH','NIFTY','SENSEX']:
    P = recover(s); v = [x for x in P['vol'] if x is not None]
    near1 = sum(1 for x in v if abs(x-1)<1e-6)/len(v)
    vs = sorted(v)
    R = P['rows']; n=len(R)
    # session starts: times of day
    st = collections.Counter(R[i]['t'][11:] for i in range(n) if P['daystart'][i])
    nonum = sum(1 for r in R if r['vwap'] is None)
    print(f"{s:7s} n={n} first={R[0]['t']} last={R[-1]['t']} bad={P['volbad']} frac_vol==1:{near1:.3f} p10={vs[len(vs)//10]:.3g} med={vs[len(vs)//2]:.3g} p90={vs[9*len(vs)//10]:.3g} vwapNone={nonum} daystarts={sum(P['daystart'])} start_times={st.most_common(4)}")
