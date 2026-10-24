import sys, io, contextlib
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/hunt2/halfstop'); sys.path.insert(0, S+'/fit')
with contextlib.redirect_stdout(io.StringIO()):
    import feat
from engine2 import prepare
for r in feat.ROWS:
    P = prepare(r['sym']); O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; j = r['j']; d = r['d']; A = m_A = None
    import m; A = m.FEAT[r['sym']][j]['A']
    mid = (O[j] + C[j]) / 2; e = max(mid, max(H[j-6:j])) if d > 0 else min(mid, min(L[j-6:j]))
    ext = d * (e - (L[j] if d > 0 else H[j])) / A
    print(f"{r['lab']} {r['src']:6s} {r['sym']:6s} {r['t']} {'L' if d>0 else 'S'} sr{r['sr']:.2f} candleExt {ext:.2f} c-vwap {d*(C[j]-V[j])/A:+.2f} with{r['withN']} pNet{r['pNet']:+d}")
