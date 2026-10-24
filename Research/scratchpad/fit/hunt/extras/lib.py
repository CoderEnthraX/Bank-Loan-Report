import sys, os, json, importlib.util
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from gtscore import load_gt, score, covered
from engine2 import prepare, run, hh, ll
from engine import rma
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
_spec = importlib.util.spec_from_file_location('rfp', FIT + '/hunt/stop_sequence/rule_firstday_prevday.py')
RFP = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(RFP)
TR, WIN = load_gt(FIT + '/../gt/final')
def cfg(**kw):
    c = dict(BEST); c['stopFn'] = RFP.stop_fn; c.update(kw); return c
def gt(sym): return sorted([t for t in TR if t['sym'] == sym], key=lambda t: t['fill'])
def full(c):
    return score(c, TR, [dict(w) for w in WIN], detail=True)
def mine(sym, c):
    P = prepare(sym); return P, run(P, c)
def sig(P, i, c=None):
    """raw displacement signal direction at bar i ignoring state (0 if none)"""
    c = c or BEST
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)][i]
    if i < 11 or A is None or A <= 0: return 0
    o, h, l, cl = O[i], H[i], L[i], C[i]; rng = h - l
    if rng <= 0 or rng < 0.8 * A or abs(cl - o) / rng * 100 < c['bodyPct']: return 0
    vw = V[i]
    bull = cl > o and (h - cl) / rng * 100 <= c['closePct'] and cl > hh(H, i, c['brkLen']) and vw is not None and cl > vw
    bear = cl < o and (cl - l) / rng * 100 <= c['closePct'] and cl < ll(L, i, c['brkLen']) and vw is not None and cl < vw
    if P['dowutc'][i] == 6: bull = bear = False
    mv = cl - C[i - 10]; bull = bull and mv >= c['momMin'] * A; bear = bear and -mv >= c['momMin'] * A
    if P['sinceStart'][i] >= 3:
        sl = V[i] - V[i - 3]; bull = bull and sl > 0; bear = bear and sl < 0
    if P['sinceStart'][i] < 1: bull = bear = False
    return 1 if bull else (-1 if bear else 0)
