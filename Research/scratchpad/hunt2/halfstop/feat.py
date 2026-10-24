import sys, io, contextlib
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/hunt2/halfstop'); sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl')
import m
with contextlib.redirect_stdout(io.StringIO()):
    import tightdata, bstops
from engine2 import prepare
cases = {}
for t in tightdata.TRADES: cases[(t['sym'], t['arm_i'])] = dict(sym=t['sym'], j=t['arm_i'], d=t['d'], lab='T' if t['tight'] else 'N', src='A', sr=t['stopR'])
BT = {45: 'T', 49: 'T', 51: 'T', 56: 'T', 52: '?', 58: 'N', 60: 'N'}
for o in bstops.OUT:
    k = (o['sym'], o['j'])
    lab = BT.get(o['n'], 'N')
    if k in cases: cases[k]['src'] += 'B%d' % o['n']; continue
    cases[k] = dict(sym=o['sym'], j=o['j'], d=o['d'], lab=lab, src='B%d' % o['n'], sr=o['sr'])
TR = {}
for sym in sorted(set(c['sym'] for c in cases.values())): TR[sym] = m.run(sym)
ROWS = []
for c in sorted(cases.values(), key=lambda c: (c['sym'], c['j'])):
    sym, j, d = c['sym'], c['j'], c['d']; P = prepare(sym); F = m.FEAT[sym][j]; O, H, L, C, T = P['O'], P['H'], P['L'], P['C'], P['T']
    s0 = F['sess']; A = F['A']
    # previous session
    ps = max(k for k in range(s0) if P['daystart'][k]) if s0 > 0 else 0
    pO, pC = O[ps], C[s0 - 1]; pH = max(H[ps:s0]); pL = min(L[ps:s0])
    prevTr = [t for t in TR[sym] if t['fill'] < j]
    lt = prevTr[-1] if prevTr else None
    sameDayTr = [t for t in prevTr if t['fill'] >= s0]
    r = dict(c, t=T[j], since=j - s0, withN=F['bullN'] if d > 0 else F['bearN'], oppN=F['bearN'] if d > 0 else F['bullN'],
             pWith=(F['prevB'] if d > 0 else F['prevS']), pOpp=(F['prevS'] if d > 0 else F['prevB']), pNet=(F['prevNet'] or 0) * d,
             withD=F['bullD'] if d > 0 else F['bearD'], oppD=F['bearD'] if d > 0 else F['bullD'],
             pMove=d * (pC - pO) / A, gap=d * (O[s0] - pC) / A, vsPC=d * (C[j] - pC) / A, vsPH=(C[j] - pH) / A if d > 0 else (pL - C[j]) / A,
             vsSO=d * (C[j] - O[s0]) / A, nDay=len(sameDayTr), ltDir=(lt['dir'] * d if lt else 0), ltRes=(lt['res'] if lt else None),
             ltAge=(j - lt['fill'] if lt else None))
    ROWS.append(r)
if __name__ == '__main__':
    for r in ROWS:
        print(f"{r['lab']} {r['src']:9s} {r['sym']:6s} {r['t']} {'L' if r['d']>0 else 'S'} sr{r['sr']:.2f} since{r['since']:3d} with{r['withN']} opp{r['oppN']} wD{r['withD']} oD{r['oppD']} pW{r['pWith']} pO{r['pOpp']} pNet{r['pNet']:+d} pMove{r['pMove']:+.1f} gap{r['gap']:+.1f} vsPC{r['vsPC']:+.1f} vsPH{r['vsPH']:+.1f} vsSO{r['vsSO']:+.1f} nDay{r['nDay']} lt{r['ltDir']:+d}/{r['ltRes']}/{r['ltAge']}")
