import sys, io, contextlib
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/hunt2/halfstop'); sys.path.insert(0, S+'/fit')
with contextlib.redirect_stdout(io.StringIO()):
    import feat
import m
from engine2 import prepare
for r in feat.ROWS:
    if r['withN'] != 0: continue
    P = prepare(r['sym']); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; j = r['j']; d = r['d']; A = m.FEAT[r['sym']][j]['A']
    s0 = m.FEAT[r['sym']][j]['sess']
    if s0 == 0: continue
    ps = max(k for k in range(s0) if P['daystart'][k]); pH = max(H[ps:s0]); pL = min(L[ps:s0]); pC = C[s0-1]
    # prev session VWAP at its close
    pV = V[s0-1]
    openOut = (O[s0] < pL) if d > 0 else (O[s0] > pH)
    nowOut = (C[j] < pL) if d > 0 else (C[j] > pH)
    sessLowBelow = (min(L[s0:j+1]) < pL) if d > 0 else (max(H[s0:j+1]) > pH)
    print(f"{r['lab']} {r['src']:6s} {r['sym']:6s} {r['t']} {'L' if d>0 else 'S'} pNet{r['pNet']:+d} openOutside {openOut} closeOutside {nowOut} sessBrokePrevExt {sessLowBelow} open-vs-pVWAP {d*(O[s0]-pV)/A:+.1f} gap% {100*d*(O[s0]-pC)/pC:+.2f}")
