"""cond.py SYM d 'YYYY-MM-DD HH:MM' ... : every displacement condition of a candidate signal bar (d=1 long, -1 short)"""
import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
sym=sys.argv[1]; d=int(sys.argv[2]); P=prepare(sym); R=P['rows']; A=rma(P['tr'],14); T=[r['t'] for r in R]; idx={t:i for i,t in enumerate(T)}
O=[r['o'] for r in R];H=[r['h'] for r in R];L=[r['l'] for r in R];C=[r['c'] for r in R];V=[r['vwap'] for r in R]
for t in sys.argv[3:]:
    i=idx[t]; a=A[i]; rng=H[i]-L[i]; body=abs(C[i]-O[i])/rng*100; ext=((H[i]-C[i]) if d>0 else (C[i]-L[i]))/rng*100
    h10=max(H[i-10:i]); l10=min(L[i-10:i]); h6=max(H[i-6:i]); l6=min(L[i-6:i])
    b10=d*(C[i]-(h10 if d>0 else l10))/a; b6=d*(C[i]-(h6 if d>0 else l6))/a
    mom=d*(C[i]-C[i-10])/a; er=d*(C[i]-C[i-10])/sum(abs(C[j]-C[j-1]) for j in range(i-9,i+1))
    mid=(O[i]+C[i])/2; ent=max(mid,h6) if d>0 else min(mid,l6); stop=ent-d*1.8*a
    print(f"{t} {'L' if d>0 else 'S'} dirOK {d*(C[i]-O[i])>0} rng/A {rng/a:.2f}(>=.8) body% {body:.0f}(>=55) ext% {ext:.0f}(<=25) brk10/A {b10:+.2f} brk6/A {b6:+.2f} mom10/A {mom:+.2f}(>=.85) ER10 {er:+.3f}(>=.2) c-vwap/A {d*(C[i]-V[i])/a:+.2f} vwSlope3/A {d*(V[i]-V[i-3])/a:+.3f} | entry {ent:.6g} stop1.8 {stop:.6g} ATR {a:.4g}")
