"""Money rules at low R: independent trades, win rate p, a win = +R x risk, a loss = -1 x risk (no costs), $1,000 start, $20 base risk,
1,000 trades, 2,000 random orders per case. Existing rules: gold/recovery.py; new rules here. Output: mm/mm_results.txt"""
import sys, random, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold')
import recovery as RC
START, BASE, NT, RUNS = 1000.0, 20.0, 1000, 2000

def run_new(rule, res, R, p):
    eq = START; peak = START; mdd = 0.0; seq = 0; hist = [START]; ruined = False
    for k, w in enumerate(res):
        if rule == '1-3-2-6': r = BASE * (1, 3, 2, 6)[seq]
        elif rule == 'Kelly 1/2':
            f = max(0.0, (p * R - (1 - p)) / R) / 2.0            # Kelly fraction of equity for a +R / -1 bet, halved
            r = eq * f
        elif rule == 'Equity-curve filter':                       # full size when equity >= its 20-trade average, else a quarter
            ma = sum(hist[-20:]) / len(hist[-20:]); r = BASE if eq >= ma else BASE * 0.25
        elif rule == 'Drawdown cut':                              # risk falls with the drawdown: half at 10% down, a quarter at 20%
            dd = (peak - eq) / peak; r = BASE * (1.0 if dd < 0.10 else 0.5 if dd < 0.20 else 0.25)
        elif rule == 'Daily stop (2 losses)':                     # base size; after 2 losses in a row skip the next 3 trades (a cooling-off)
            if seq < 0: seq += 1; hist.append(eq); continue
            r = BASE
        if r <= 0: hist.append(eq); continue
        r = min(r, eq)
        pnl = r * R if w else -r
        eq += pnl; peak = max(peak, eq); mdd = max(mdd, peak - eq); hist.append(eq)
        if rule == '1-3-2-6': seq = (seq + 1) % 4 if w else 0
        if rule == 'Daily stop (2 losses)':
            seq = 0 if w else (seq + 1 if seq >= 0 else seq)
            if seq >= 2: seq = -3
        if eq <= 1.0: ruined = True; break
    return eq - START, mdd, ruined

def run_old(mode, res, R, extra):
    trs = [((R if w else -1.0), 0.0, None, None, None, 1.0) for w in res]
    r = RC.simulate(trs, mode, base=BASE, exitR=R, start=START, **extra)
    return r['net'], r['maxDD'], r['ruined']

OLD = [('Fixed $20 (Off)', 'Off', {}), ('Over N = 3', 'Recover losses over N trades', dict(recN=3)), ('Martingale', 'Martingale (multiply after each loss)', {}),
       ("D'Alembert", "D'Alembert", {}), ('Paroli (3)', 'Paroli', {}), ("Reverse D'Alembert", "Reverse D'Alembert", {}), ("Oscar's Grind", "Oscar's Grind", {}),
       ('Crooks E, N = 3', 'Crooks E', dict(cN=3)), ('Crooks X, N = 3', 'Crooks X', dict(cN=3)), ('% of equity (2%)', '% of equity', dict(eqPct=2.0))]
NEW = ['1-3-2-6', 'Kelly 1/2', 'Equity-curve filter', 'Drawdown cut', 'Daily stop (2 losses)']
out = []
for p in (0.70, 0.80, 0.90):
    for R in (0.1, 0.2, 0.3, 0.5):
        rng = random.Random(int(p * 100) * 10 + int(R * 10)); seqs = [[rng.random() < p for _ in range(NT)] for _ in range(RUNS)]
        ev = p * R - (1 - p); be = 1.0 / (1.0 + R)
        out.append('\nwin rate %.0f%%, target %.1fR: expectancy per trade %+.3fR (break-even win rate %.1f%%)' % (p * 100, R, ev, be * 100))
        out.append('  %-26s %10s %10s %9s %8s %s' % ('rule', 'median net', 'mean net', 'avg maxDD', 'ruined', 'kind'))
        for name, mode, extra in OLD:
            rs = [run_old(mode, s, R, extra) for s in seqs[:400]]
            out.append('  %-26s %10.0f %10.0f %9.0f %7.1f%% in the strategy' % (name, st.median(x[0] for x in rs), st.mean(x[0] for x in rs), st.mean(x[1] for x in rs), 100 * sum(x[2] for x in rs) / len(rs)))
        for name in NEW:
            rs = [run_new(name, s, R, p) for s in seqs]
            out.append('  %-26s %10.0f %10.0f %9.0f %7.1f%% NEW' % (name, st.median(x[0] for x in rs), st.mean(x[0] for x in rs), st.mean(x[1] for x in rs), 100 * sum(x[2] for x in rs) / len(rs)))
open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mm/mm_results.txt', 'w').write('\n'.join(out))
print('\n'.join(out))
