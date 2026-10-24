import sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from rec import *
from sig import raw
from tightdata import TRADES
for t in TRADES:
    P = prepare(t['sym']); S = raw(P); i = t['arm_i']; d = t['d']; A = P[('atr',14)][i]
    O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']
    ds = i - P['sinceStart'][i]
    same = [j for j in range(ds, i) if S[j] == d]; opp = [j for j in range(ds, i) if S[j] == -d]
    if same: continue
    dayO = O[ds]; pdc = C[ds - 1]
    hod = max(H[ds:i]) if i > ds else H[i]; lod = min(L[ds:i]) if i > ds else L[i]
    print(f"{t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} {'TIGHT' if t['tight'] else '     '} since={P['sinceStart'][i]:3d} opp={len(opp)} "
          f"dOpen={d*(C[i]-dayO)/A:5.2f} dPDC={d*(C[i]-pdc)/A:5.2f} dVW={d*(C[i]-V[i])/A:5.2f} rng={(H[i]-L[i])/A:4.2f} "
          f"brkExt={d*(C[i]-(hod if d>0 else lod))/A:5.2f} dayRng={(hod-lod)/A:5.2f} gapO={d*(dayO-pdc)/A:5.2f} entryVsExt={d*(t['entry']-(L[i] if d>0 else H[i]))/A:4.2f}")
