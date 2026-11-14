"""End to end: the twin with Money on (random money settings, the hard cap's Stop trading included) on M15 chart candles vs engine2 trades
(cut where the twin's strategy stopped) and recovery.py's risks on those trades. Usage: parity2_e2e.py SEED N"""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/gold')
import engine as EN, engine2 as E2, pine_twin2 as TW, recovery as RC
from final11 import ALL
B = EN.load(); rng = np.random.default_rng(int(sys.argv[1])); bad = 0; tot = 0
for it in range(int(sys.argv[2])):
    prm = ALL[int(rng.integers(len(ALL)))]
    if prm[0] == 'M5': prm = ALL[3]
    m = int(rng.integers(28))
    kw = dict(mmOn=True, recMode=m, capOn=True, hardCap=float(rng.choice([150.0, 300.0, 500.0])), capAction=str(rng.choice(['clamp', 'stop', 'reset'])),
              lad=str(rng.choice(['Off', 'Medium', 'Max'])), ladT=300.0, startB=float(rng.choice([10000.0, 1000.0])), crkPr=str(rng.choice(['off', 'forget', 'wait'])))
    p = TW.P(**kw); s = TW.twin2(B, 'M15', prm, p)
    ref = E2.run2(B, 'M15', *prm)[:len(s.trades)]
    same = len(s.trades) <= len(E2.run2(B, 'M15', *prm)) and all(a[0] == int(b[0]) and a[1] == b[1] and a[2] == int(b[2]) and a[3] == b[3] and a[4] == int(b[4]) for a, b in zip(s.trades, ref))
    sl, tp = prm[4], prm[5]; trs = []
    for x in ref:
        F, X = x[1], x[3]; sd = F * sl / 100.0
        trs.append(((X - F) / sd, p.costIn / sd, None, None, p.levIn * (sd + p.costIn) / F, p.eUnits * (sd + p.costIn)))
    tr = []
    r = RC.simulate(trs, RC.MODES[m], base=p.baseR, cap=p.hardCap, capAction=p.capAction, exitR=tp / sl, start=p.startB, trace=tr, cN=p.crkCn, crkPr=p.crkPr,
                    fK=p.crkFK, gX=p.crkGX, hPct=p.crkHPct, jX=p.crkJX, lad=None if p.lad == 'Off' else p.lad, ladT=p.ladT, cSplit=p.cSplit)
    okr = len(tr) == len(s.risks) and all(abs(a - b) <= 1e-9 * max(1.0, abs(a)) for a, b in zip(tr, s.risks))
    stopped = s.stopped
    tot += len(s.trades); bad += 0 if (same and okr) else 1
    if not (same and okr):
        print('DIFF', prm[:3], RC.MODES[m], kw['capAction'], 'trades same', same, 'risks same', okr, len(tr), len(s.risks), 'stopped', stopped)
print('end to end (M15, money on): %d random settings, %d trades, %s' % (it + 1, tot, 'ALL IDENTICAL' if bad == 0 else '%d DIFFERENT' % bad))
