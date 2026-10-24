"""Is the CSV VWAP volume-weighted? Compare with time-weighted hlc3 / close cumulative means per session; implied volume."""
import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit')
from engine2 import prepare
for sym in ('SENSEX', 'CRUDE', 'NIFTY'):
    P = prepare(sym); O,H,L,C,V,T,D = P['O'],P['H'],P['L'],P['C'],P['V'],P['T'],P['daystart']
    n = len(T); errh = []; errc = []; sh = sc = k = 0; impl = []
    for i in range(n):
        if D[i]: sh = sc = k = 0
        hl = (H[i]+L[i]+C[i])/3; sh += hl; sc += C[i]; k += 1
        if V[i] is None: continue
        errh.append(abs(V[i]-sh/k)); errc.append(abs(V[i]-sc/k))
        # implied relative volume of bar i: V_i = (cum_pv)/(cum_v) -> w_i/(W_{i-1}+w_i) = (V_i - V_{i-1})/(hl - V_{i-1})
        if not D[i] and abs(hl - V[i-1]) > 1e-6: impl.append((T[i], (V[i]-V[i-1])/(hl-V[i-1])))
    errh.sort(); errc.sort()
    print(sym, 'bars', n, 'sessions', sum(D), '| |VWAP - twap(hlc3)| median %.4g max %.4g' % (errh[len(errh)//2], errh[-1]), '| twap(close) median %.4g' % errc[len(errc)//2])
    # session start times
    from collections import Counter
    print('   session first-bar times:', Counter(T[i][11:] for i in range(n) if D[i]).most_common(5), 'last-bar times:', Counter(T[i-1][11:] for i in range(1,n) if D[i]).most_common(5))
    print('   implied w_i/W_i sample:', [(t, round(f, 4)) for t, f in impl[100:106]])
