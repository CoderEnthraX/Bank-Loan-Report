"""stateless displacement signal series (best-model criteria) + previous-displacement features"""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
def dser(P, brk=10, body=55, cp=25, rngA=0.8, mom=0.85, lag=3, relax=None):
    key = ('dser', brk, body, cp, rngA, mom, lag)
    if key in P: return P[key]
    O,H,L,C,V = P['O'],P['H'],P['L'],P['C'],P['V']; A = P[('atr',14)]; n = len(O); out = [0]*n
    for i in range(12, n):
        a = A[i]
        if a is None or V[i] is None: continue
        rng = H[i]-L[i]
        if rng <= 0 or rng < rngA*a: continue
        bd = abs(C[i]-O[i])
        if bd/rng*100 < body: continue
        if P['daystart'][i]: continue
        if P['dowutc'][i] == 6: continue
        ok_l = C[i] > O[i] and (H[i]-C[i])/rng*100 <= cp and C[i] > max(H[i-brk:i]) and C[i] > V[i] and C[i]-C[i-10] >= mom*a
        ok_s = C[i] < O[i] and (C[i]-L[i])/rng*100 <= cp and C[i] < min(L[i-brk:i]) and C[i] < V[i] and C[i-10]-C[i] >= mom*a
        if P['sinceStart'][i] >= lag:
            ok_l = ok_l and V[i] > V[i-lag]; ok_s = ok_s and V[i] < V[i-lag]
        out[i] = 1 if ok_l else (-1 if ok_s else 0)
    P[key] = out; return out
def pfeat(P, i, d, entry, A):
    s = dser(P); sessions(P); g = {}
    same = [j for j in range(max(0, i-300), i) if s[j] == d]; opp = [j for j in range(max(0, i-300), i) if s[j] == -d]
    g['bs_same'] = i - same[-1] if same else 999; g['bs_opp'] = i - opp[-1] if opp else 999
    ss = P['sess'][i]
    g['n_same_sess'] = sum(1 for j in same if j >= ss); g['n_opp_sess'] = sum(1 for j in opp if j >= ss)
    for N in (6, 12, 24, 48):
        g[f'n_same{N}'] = sum(1 for j in same if j >= i-N); g[f'n_opp{N}'] = sum(1 for j in opp if j >= i-N)
    if same:
        j = same[-1]; nx = lambda v: d*(v-entry)/A
        g['ps_lo'] = nx(L[j] if False else (P['L'][j] if d > 0 else P['H'][j])); g['ps_mid'] = nx((P['O'][j]+P['C'][j])/2); g['ps_c'] = nx(P['C'][j]); g['ps_o'] = nx(P['O'][j])
    if opp:
        j = opp[-1]; nx = lambda v: d*(v-entry)/A
        g['po_ext'] = nx(P['H'][j] if d > 0 else P['L'][j]); g['po_mid'] = nx((P['O'][j]+P['C'][j])/2)
    return g
if __name__ == '__main__':
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
        rows.append((t, pfeat(P, i, t['d'], t['entry'], A)))
    keys = sorted({k for _, x in rows for k in x})
    for k in keys:
        vals = sorted([(x.get(k), t['tight'], t) for t, x in rows if x.get(k) is not None], key=lambda r: r[0])
        print(k, ' '.join(('T' if tg else '.') for _, tg, _ in vals))
        print('   tight vals', [round(v, 2) for v, tg, _ in vals if tg], 'n', len(vals), 'normal range', round(min(v for v,tg,_ in vals if not tg),2), round(max(v for v,tg,_ in vals if not tg),2))
