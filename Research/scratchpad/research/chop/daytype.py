"""HINDSIGHT day-type features per session (uses the whole session) + bar -> session map."""
import sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine2 import prepare
from engine import rma
_C = {}
def crosses(dev, hyst):
    """number of VWAP crosses: sign changes of dev (C-V in ATR) with a hysteresis band"""
    s = 0; n = 0
    for v in dev:
        if v > hyst: z = 1
        elif v < -hyst: z = -1
        else: continue
        if s and z != s: n += 1
        s = z
    return n
def sessions(sym):
    if sym in _C: return _C[sym]
    P = prepare(sym); O, H, L, C, V, T = P['O'], P['H'], P['L'], P['C'], P['V'], P['T']; A = rma(P['tr'], 14); n = len(C)
    st = [i for i in range(n) if P['daystart'][i]]
    if not st or st[0] != 0: st = [0] + st
    out = []; sidx = [0] * n
    for k, a in enumerate(st):
        b = (st[k + 1] if k + 1 < len(st) else n) - 1
        for i in range(a, b + 1): sidx[i] = k
        ats = [A[i] for i in range(a, b + 1) if A[i]]
        if not ats or b - a < 10: out.append(None); continue
        am = sum(ats) / len(ats)
        hi = max(H[a:b + 1]); lo = min(L[a:b + 1]); rg = hi - lo
        dev = [(C[i] - V[i]) / (A[i] or am) for i in range(a, b + 1)]
        nb = b - a + 1
        d = dict(k=k, a=a, b=b, date=T[a][:10], nb=nb, first=(k == 0),
                 eff=abs(C[b] - O[a]) / rg if rg else 0, rngA=rg / am,
                 x0=crosses(dev, 0.0), x2=crosses(dev, 0.2), x0r=crosses(dev, 0.0) / nb * 100,
                 near05=sum(abs(v) <= 0.5 for v in dev) / nb, near1=sum(abs(v) <= 1.0 for v in dev) / nb,
                 clV=abs(C[b] - V[b]) / am, clLoc=(C[b] - lo) / rg if rg else 0.5)
        out.append(d)
    _C[sym] = (out, sidx); return _C[sym]
