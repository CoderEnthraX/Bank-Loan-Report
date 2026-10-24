import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
sym, a, b = sys.argv[1:4]; d = int(sys.argv[4]) if len(sys.argv) > 4 else 0
P = prepare(sym); R = P['rows']; A = rma(P['tr'], 14)
H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; O = [r['o'] for r in R]; V = [r['vwap'] for r in R]
for i, r in enumerate(R):
    if a <= r['t'] <= b:
        rng = H[i]-L[i]; ph = max(H[i-10:i]); pl = min(L[i-10:i]); a_ = A[i]
        bodyP = abs(C[i]-O[i])/rng*100 if rng else 0
        clP = ((H[i]-C[i]) if C[i]>O[i] else (C[i]-L[i]))/rng*100 if rng else 0
        mom = (C[i]-C[i-10])/a_
        sl = V[i]-V[i-3]
        print(r['t'], 'o %.6g h %.6g l %.6g c %.6g vw %.6g' % (O[i],H[i],L[i],C[i],V[i]), 'rngA %.2f body %.0f cl %.0f' % (rng/a_, bodyP, clP),
              'brkH %+.2f brkL %+.2f' % ((C[i]-ph)/a_, (pl-C[i])/a_), 'mom %+.2f sl %+.3g' % (mom, sl), 'DS' if P['daystart'][i] else '')
