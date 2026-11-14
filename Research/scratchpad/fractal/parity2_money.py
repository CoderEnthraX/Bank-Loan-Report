"""Money: the Pine twin v2's mmOpen / mmBook (the Pine code) vs gold/recovery.py simulate, the $ risk of every trade and the final net, on the
11 strategies' real gold trades, every loss-recovery mode and option combination (caps, ladder, Crooks C over N wins and the rule after N
losing recovery trades, E / I lot), randomly drawn. Usage: parity2_money.py SEED N"""
import sys, math, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/gold')
import engine as EN, pine_twin2 as TW, recovery_tol as RC
from final11 import ALL
B = EN.load(); TR = {k: EN.run(B, 'M1', *p) for k, p in enumerate(ALL)}
rng = np.random.default_rng(int(sys.argv[1])); bad = 0; nt = 0; worst = 0.0
for it in range(int(sys.argv[2])):
    k = int(rng.integers(len(ALL))); prm = ALL[k]; tr = TR[k]; sl, tp = prm[4], prm[5]
    m = int(rng.integers(28))
    kw = dict(recMode=m, baseR=float(rng.choice([50.0, 25.0, 100.0])), startB=float(rng.choice([10000.0, 2000.0, 500.0])), costIn=float(rng.choice([0.23, 0.0, 0.5])),
              capOn=bool(rng.random() < 0.6), hardCap=float(rng.choice([250.0, 500.0, 1000.0])), capAction=str(rng.choice(['clamp', 'stop', 'reset'])),
              lad=str(rng.choice(['Off', 'Low', 'Medium', 'High', 'Extra high', 'Max'])), ladT=float(rng.choice([300.0, 1000.0])),
              recN=int(rng.choice([2, 3, 5])), recPct=float(rng.choice([30.0, 50.0])), recMult=float(rng.choice([1.5, 2.0])), recStep=float(rng.choice([10.0, 25.0])),
              cSplit=int(rng.choice([1, 2, 3])), parN=int(rng.choice([2, 3])), delayN=int(rng.choice([1, 2, 3])), eqPct=float(rng.choice([0.5, 1.0, 2.0])),
              crkCn=int(rng.choice([1, 1, 2, 3])), crkPr=str(rng.choice(['off', 'off', 'forget', 'pct', 'wait'])), crkPrN=int(rng.choice([1, 2, 3])),
              crkPrPct=float(rng.choice([30.0, 50.0])), crkPrM=int(rng.choice([1, 2])), crkELot=float(rng.choice([0.01, 0.02])), crkFK=float(rng.choice([2.0, 3.0, 5.0])),
              crkGX=float(rng.choice([5.0, 10.0])), crkHPct=float(rng.choice([1.0, 2.0])), crkJX=float(rng.choice([10.0, 20.0])), levIn=float(rng.choice([100.0, 30.0])))
    p = TW.P(**kw); s = TW.Strat(p, 0, prm[3], sl, tp, prm[6], prm[7])
    risks = []
    for x in tr:
        F, X = x[1], x[3]
        if s.stopped: break
        if not s.mmOpen(F): break
        risks.append(s.risk); s.mmBook(s.units * (X - F - p.costIn))
    # recovery.py with the same trades
    trs = []
    for x in tr:
        F, X = x[1], x[3]; sd = F * sl / 100.0; c = p.costIn / sd
        trs.append(((X - F) / sd, c, None, None, p.levIn * (sd + p.costIn) / F, p.eUnits * (sd + p.costIn)))
    ref = []
    r = RC.simulate(trs, RC.MODES[m], base=p.baseR, cap=p.hardCap if p.capOn else 0.0, capAction=p.capAction, exitR=tp / sl, start=p.startB, recN=p.recN, recPct=p.recPct,
                    mult=p.recMult, step=p.recStep, cSplit=p.cSplit, parN=p.parN, delayN=p.delayN, eqPct=p.eqPct, trace=ref, cN=p.crkCn, crkPr=p.crkPr, crkPrN=p.crkPrN,
                    crkPrPct=p.crkPrPct, crkPrM=p.crkPrM, fK=p.crkFK, gX=p.crkGX, hPct=p.crkHPct, jX=p.crkJX, lad=None if p.lad == 'Off' else p.lad, ladT=p.ladT)
    ref = [x for x in ref if x != 'SKIP']
    n = min(len(ref), len(risks)); d = max([abs(a - b) / max(1.0, abs(a)) for a, b in zip(ref, risks)] or [0.0]); nt += n; worst = max(worst, d)
    dn = abs(r['net'] - s.net) / max(1.0, abs(r['net']))
    if len(ref) != len(risks) or d > 1e-9 or dn > 1e-7:
        bad += 1
        q = next((i for i, (a, b) in enumerate(zip(ref, risks)) if abs(a - b) / max(1.0, abs(a)) > 1e-9), n)
        print('MISMATCH S%d %s %s | ref %d trades, twin %d | first diff at %d: ref %s twin %s | net ref %.4f twin %.4f' % (
            k + 1, RC.MODES[m], {a: kw[a] for a in ('capOn', 'capAction', 'lad', 'crkCn', 'crkPr', 'startB')}, len(ref), len(risks), q, ref[q] if q < len(ref) else None,
            risks[q] if q < len(risks) else None, r['net'], s.net))
print('money: %d random settings, %d trades compared, mismatches %d, worst relative difference %.1e' % (it + 1, nt, bad, worst))
