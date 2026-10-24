"""Price-level feature table for the 80 original trades."""
import sys, math
FIT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from engine import rma
from tightdata import TRADES
from volrec import recover

def sessions(P):
    """per bar: session index, session start index"""
    if 'sess' in P: return
    n = len(P['O']); ss = [0]*n; k = 0
    for i in range(n):
        if P['daystart'][i]: k = i
        ss[i] = k
    P['sess'] = ss
    # prev session HLC per start
    starts = [i for i in range(n) if P['daystart'][i]]
    prev = {}
    for a, b in zip(starts, starts[1:]):
        prev[b] = (max(P['H'][a:b]), min(P['L'][a:b]), P['C'][b-1], P['O'][a], a)
    P['prevsess'] = prev; P['starts'] = starts

def levels(P, i, d, entry, A):
    sessions(P); recover(P['sym'])
    O,H,L,C,V = P['O'],P['H'],P['L'],P['C'],P['V']
    s = P['sess'][i]; f = {}
    f['vwap'] = V[i]; sd = P['vsd'][i] or 0
    for k in (1,2,3): f[f'vu{k}'] = V[i]+k*sd; f[f'vd{k}'] = V[i]-k*sd
    f['sopen'] = O[s]; f['shi'] = max(H[s:i+1]); f['slo'] = min(L[s:i+1])
    f['shi_x'] = max(H[s:i]) if i > s else H[i]; f['slo_x'] = min(L[s:i]) if i > s else L[i]
    pv = P['prevsess'].get(s)
    if pv: f['pdh'], f['pdl'], f['pdc'], f['pdo'] = pv[:4]
    for N in (1,2,3,6,12):
        if i >= s+N-1: f[f'orh{N}'] = max(H[s:s+N]); f[f'orl{N}'] = min(L[s:s+N])
    f['dO'],f['dH'],f['dL'],f['dC'] = O[i],H[i],L[i],C[i]
    return f

def nlevels(P, i, d, entry, A):
    """direction-normalised: fav = profit side (high for long), adv = stop side. values = d*(level-entry)/A"""
    f = levels(P, i, d, entry, A); g = {}
    def nx(v): return None if v is None else d*(v-entry)/A
    g['vwap'] = nx(f['vwap'])
    for k in (1,2,3):
        g[f'bf{k}'] = nx(f[f'vu{k}'] if d > 0 else f[f'vd{k}']); g[f'ba{k}'] = nx(f[f'vd{k}'] if d > 0 else f[f'vu{k}'])
    g['sopen'] = nx(f['sopen'])
    g['sfav'] = nx(f['shi'] if d > 0 else f['slo']); g['sadv'] = nx(f['slo'] if d > 0 else f['shi'])
    g['sfavx'] = nx(f['shi_x'] if d > 0 else f['slo_x']); g['sadvx'] = nx(f['slo_x'] if d > 0 else f['shi_x'])
    if 'pdh' in f:
        g['pdfav'] = nx(f['pdh'] if d > 0 else f['pdl']); g['pdadv'] = nx(f['pdl'] if d > 0 else f['pdh']); g['pdc'] = nx(f['pdc']); g['pdo'] = nx(f['pdo'])
        g['pdmid'] = nx((f['pdh']+f['pdl'])/2)
    for N in (1,2,3,6,12):
        if f'orh{N}' in f:
            g[f'orfav{N}'] = nx(f[f'orh{N}'] if d > 0 else f[f'orl{N}']); g[f'oradv{N}'] = nx(f[f'orl{N}'] if d > 0 else f[f'orh{N}'])
    g['dExtAdv'] = nx(f['dL'] if d > 0 else f['dH'])
    g['srange'] = (f['shi']-f['slo'])/A
    g['since'] = P['sinceStart'][i]
    return g

def rlevels(P, i, d, entry, A):
    """round-number distances: nearest round level on fav side (>entry for long) and adverse side, ATR units, several steps"""
    g = {}
    mag = 10 ** math.floor(math.log10(abs(entry)))
    for k in (1, 2, 3):
        for m in (1, 2, 2.5, 5):
            st = mag / 10 ** k * m
            up = math.ceil(entry / st) * st; dn = math.floor(entry / st) * st
            fav = up if d > 0 else dn; adv = dn if d > 0 else up
            g[f'rf{k}_{m}'] = d * (fav - entry) / A; g[f'ra{k}_{m}'] = d * (adv - entry) / A
    return g

def wlevels(P, i, d, entry, A):
    """weekly (UTC Monday) open / prior-week high-low; ISO week of the session start"""
    import datetime as dt
    if 'wk' not in P:
        sessions(P)
        wk = []
        for j in range(len(P['T'])):
            t = dt.datetime.strptime(P['T'][P['sess'][j]], '%Y-%m-%d %H:%M') - dt.timedelta(hours=5, minutes=30) + dt.timedelta(hours=6)
            wk.append(t.isocalendar()[:2])
        P['wk'] = wk
        first = {}; hi = {}; lo = {}
        for j, w in enumerate(wk):
            first.setdefault(w, j); hi[w] = max(hi.get(w, -1e18), P['H'][j]); lo[w] = min(lo.get(w, 1e18), P['L'][j])
        P['wkfirst'] = first; P['wkhi'] = hi; P['wklo'] = lo
    w = P['wk'][i]; ws = sorted(P['wkfirst']); g = {}
    nx = lambda v: d * (v - entry) / A
    g['wopen'] = nx(P['O'][P['wkfirst'][w]])
    a = P['wkfirst'][w]
    g['wfav'] = nx(max(P['H'][a:i+1]) if d > 0 else min(P['L'][a:i+1])); g['wadv'] = nx(min(P['L'][a:i+1]) if d > 0 else max(P['H'][a:i+1]))
    k = ws.index(w)
    if k > 0:
        pw = ws[k-1]; g['pwfav'] = nx(P['wkhi'][pw] if d > 0 else P['wklo'][pw]); g['pwadv'] = nx(P['wklo'][pw] if d > 0 else P['wkhi'][pw])
    return g

def allfeat(P, i, d, entry, A):
    g = nlevels(P, i, d, entry, A); g.update(rlevels(P, i, d, entry, A)); g.update(wlevels(P, i, d, entry, A))
    return g

def adrfeat(P, i, d, entry, A):
    sessions(P)
    st = P['starts']; s = P['sess'][i]; k = st.index(s); g = {}
    O,H,L,C = P['O'],P['H'],P['L'],P['C']
    shi = max(H[s:i+1]); slo = min(L[s:i+1])
    rngs = []; trs = []
    for a, b in zip(st[:k], st[1:k+1]):
        hi, lo = max(H[a:b]), min(L[a:b]); rngs.append(hi-lo)
        pc = C[a-1] if a > 0 else None
        trs.append(max(hi-lo, abs(hi-pc), abs(lo-pc)) if pc is not None else hi-lo)
    for N in (5, 10, 14, 20):
        if len(rngs) >= N:
            adr = sum(rngs[-N:])/N; datr = sum(trs[-N:])/N
            for nm, X in (('adr', adr), ('datr', datr)):
                pf = (slo + X) if d > 0 else (shi - X)      # projected fav extreme
                pa = (shi - X) if d > 0 else (slo + X)      # projected adverse extreme
                g[f'{nm}{N}_roomf'] = d*(pf-entry)/A; g[f'{nm}{N}_rooma'] = d*(pa-entry)/A
                g[f'{nm}{N}_used'] = (shi-slo)/X; g[f'{nm}{N}_xa'] = X/A
    return g
_af = allfeat
def allfeat(P, i, d, entry, A):
    g = _af(P, i, d, entry, A); g.update(adrfeat(P, i, d, entry, A)); return g
