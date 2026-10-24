"""Raw displacement signals (all price conditions of BEST, no state) per bar: +1/-1/0."""
import sys
FIT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
def raw(P, brk=10, body=55, cl_=25, disp=0.8, mom=0.85, vs=3):
    key = ('rawsig', brk, body, cl_, disp, mom, vs)
    if key in P: return P[key]
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)]; n = len(O); out = [0] * n
    for i in range(11, n):
        a = A[i]
        if a is None or a <= 0: continue
        o, h, l, c = O[i], H[i], L[i], C[i]; rng = h - l
        if rng <= 0 or rng < disp * a or abs(c - o) / rng * 100 < body: continue
        if P['sinceStart'][i] < 1 or P['dowutc'][i] == 6: continue
        vw = V[i]
        bull = c > o and (h - c) / rng * 100 <= cl_ and c > max(H[i - brk:i]) and vw is not None and c > vw and c - C[i - 10] >= mom * a
        bear = c < o and (c - l) / rng * 100 <= cl_ and c < min(L[i - brk:i]) and vw is not None and c < vw and C[i - 10] - c >= mom * a
        if P['sinceStart'][i] >= vs:
            bull = bull and V[i] - V[i - vs] > 0; bear = bear and V[i] - V[i - vs] < 0
        out[i] = 1 if bull else (-1 if bear else 0)
    P[key] = out; return out
