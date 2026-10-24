import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
from lib import *
from tightdata import TRADES
from volrec import recover
NEG = [('CRUDE','2026-10-06 20:55',1),('CRUDE','2026-10-06 21:30',1),('ETH','2026-10-10 03:30',-1),('ETH','2026-10-11 00:05',1),('NIFTY','2026-10-07 09:35',-1),
       ('US30','2026-10-07 07:30',-1),('US30','2026-10-07 16:10',-1),('US30','2026-10-07 18:00',-1),('NASDAQ','2026-10-12 06:55',-1)]
def F(P, i, d):
    O,H,L,C,V,T = P['O'],P['H'],P['L'],P['C'],P['V'],P['T']; A = P[('atr',14)][i]
    o,h,l,c = O[i],H[i],L[i],C[i]; rng = h-l
    recover(P['sym']); vol = P['vol']; vsd = P['vsd']
    hi10 = max(H[i-10:i]); lo10 = min(L[i-10:i])
    lvl = hi10 if d>0 else lo10
    e = max((o+c)/2, max(H[i-6:i])) if d>0 else min((o+c)/2, min(L[i-6:i]))
    f = {}
    f['rngA'] = rng/A; f['bodyA'] = abs(c-o)/A; f['bodyP'] = abs(c-o)/rng; f['closeP'] = ((h-c) if d>0 else (c-l))/rng
    f['brkA'] = d*(c-lvl)/A; f['brk_rng'] = d*(c-lvl)/rng; f['ht10A'] = (hi10-lo10)/A; f['brk_ht'] = d*(c-lvl)/(hi10-lo10)
    f['momA'] = d*(c-C[i-10])/A; f['vslA'] = d*(V[i]-V[i-3])/A if P['sinceStart'][i]>=3 else 99
    f['cvwA'] = d*(c-V[i])/A; f['z'] = d*(c-V[i])/vsd[i] if vsd[i] else 0; f['evwA'] = d*(e-V[i])/A
    f['openVsLvlA'] = d*(o-lvl)/A
    pv = vol[i-20:i]; pv = [x for x in pv if x is not None]
    f['rvol'] = (vol[i] or 0)/(sum(pv)/len(pv)) if pv and sum(pv)>0 else 0
    ph, pl = H[i-1], L[i-1]; ov = max(0, min(h,ph)-max(l,pl)); f['ovPrev'] = ov/rng
    f['prevDir'] = d*(C[i-1]-O[i-1])/A
    # bars since last close beyond prior 10-bar extreme in dir d
    k = None
    for j in range(i-1, max(11, i-200), -1):
        if (C[j] > max(H[j-10:j])) if d>0 else (C[j] < min(L[j-10:j])): k = i-j; break
    f['sinceBrk'] = k if k else 999
    k = None
    for j in range(i-1, max(11, i-300), -1):
        if sig(P, j) == d: k = i-j; break
    f['sinceSig'] = k if k else 999
    k = None
    for j in range(i-1, max(11, i-300), -1):
        if sig(P, j) == -d: k = i-j; break
    f['sinceOpp'] = k if k else 999
    f['since'] = P['sinceStart'][i]
    f['entryVsC'] = d*(c-e)/A
    f['wickA'] = ((o-l) if d>0 else (h-o))/A
    f['dist20'] = d*(c - (sum(C[i-20:i])/20))/A
    # sum of directional bodies of last 10 bars
    f['run10'] = sum(1 for j in range(i-10,i) if d*(C[j]-O[j])>0)
    f['bal10'] = (max(C[i-10:i])-min(C[i-10:i]))/A
    return f
rows = []
for t in TRADES:
    P = prepare(t['sym']); rows.append(('POS', t['sym'], t['arm'], t['d'], F(P, t['arm_i'], t['d'])))
for s, a, d in NEG:
    P = prepare(s); i = P['T'].index(a); rows.append(('NEG', s, a, d, F(P, i, d)))
import pickle; pickle.dump(rows, open('feat.pkl','wb'))
keys = list(rows[0][4].keys())
for k in keys:
    pos = sorted(r[4][k] for r in rows if r[0]=='POS')
    neg = [(r[1][:3]+r[2][5:], round(r[4][k],3)) for r in rows if r[0]=='NEG']
    print(f"{k:10s} POS min {pos[0]:.3f} p5 {pos[4]:.3f} med {pos[40]:.3f} p95 {pos[-5]:.3f} max {pos[-1]:.3f} | NEG {neg}")
