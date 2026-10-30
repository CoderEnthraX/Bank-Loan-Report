"""Re-size the trades of a TradingView trade list (TP2 exit, one row per trade) with Crooks C, old rule (a winning recovery trade starts
over) or new rule (a leftover stays owed). The signals do not depend on the sizing, so each trade keeps its entry, exit and stop:
planned stop = |exit - entry| for a win (TP2 = 1R), |exit - entry| - slippage for a stop-out. Size = floor(risk / stop), cut to
equity x leverage / price, commission per unit round trip. Usage: whatif.py FILE [capital lev comm slip cap]"""
import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
def sim(tr, rule, capital=100000.0, lev=100.0, comm=0.07, slip=0.10, base=50.0, exitR=1.0, cap=0.0, act='reset'):
    eq = capital; L = 0.0; W = False; out = []; peak = capital; mdd = 0.0; maxRisk = 0.0
    for t in tr:
        rec = W and L > 0
        risk = max(base, L / exitR) if rec else base
        if cap > 0 and risk > cap:
            if act == 'reset': L = 0.0; W = False; rec = False; risk = base
            else: risk = cap
        move = t['dir'] * (t['exit_px'] - t['entry_px'])
        rp = abs(t['exit_px'] - t['entry_px']) - (slip if t['pnl'] < 0 else 0.0)
        q = math.floor(risk / rp + 1e-9) if rp > 0 else 0
        qlev = math.floor(eq * lev / t['entry_px'] + 1e-9) if lev > 0 else q
        q = min(q, qlev)
        pnl = q * move - comm * q
        out.append(dict(n=t['n'], q=q, pnl=pnl, owed=L, rec=rec, risk=risk, capped=q == qlev and qlev < math.floor(risk / rp + 1e-9)))
        eq += pnl; peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak); maxRisk = max(maxRisk, risk)
        win = pnl > 0
        L = max(0.0, L - pnl)
        if L < 0.01 or (rule == 'old' and win and rec): L = 0.0
        W = win
        if eq <= 0: break
    return out, eq, mdd, maxRisk
if __name__ == '__main__':
    tr = load(sys.argv[1])
    old, eqo, ddo, mro = sim(tr, 'old')
    err = [abs(a['pnl'] - t['pnl']) for a, t in zip(old, tr)]
    print('old rule replayed: end P&L %+.0f (the file: %+.0f); trades within $1 of the file: %d of %d, within $5: %d, worst difference $%.0f' % (
        eqo - 100000, sum(t['pnl'] for t in tr), sum(1 for e in err if e <= 1), len(tr), sum(1 for e in err if e <= 5), max(err)))
    new, eqn, ddn, mrn = sim(tr, 'new')
    print('new rule: end P&L %+.0f, deepest fall %.0f%%, largest planned risk $%.0f, trades %d of %d (account blown: %s)' % (eqn - 100000, 100 * ddn, mrn, len(new), len(tr), eqn <= 0))
    print('old rule: end P&L %+.0f, deepest fall %.0f%%, largest planned risk $%.0f' % (eqo - 100000, 100 * ddo, mro))
    for a in new[79:90]:
        print('   #%d %-8s owed %8.0f planned risk %8.0f qty %6d P&L %+8.0f %s' % (a['n'], 'RECOVERY' if a['rec'] else 'base', a['owed'], a['risk'], a['q'], a['pnl'], '(cut by leverage)' if a['capped'] else ''))
    for cap in (500.0,):
        for act in ('reset', 'clamp'):
            o, e1, d1, m1 = sim(tr, 'old', cap=cap, act=act); n, e2, d2, m2 = sim(tr, 'new', cap=cap, act=act)
            print('with a $%.0f hard cap (%s): old rule %+.0f (fall %.0f%%), new rule %+.0f (fall %.0f%%)' % (cap, act, e1 - 100000, 100 * d1, e2 - 100000, 100 * d2))
    f, ef, df, mf = sim(tr, 'old', base=50.0, exitR=1.0, cap=50.0, act='clamp')
    print('fixed $50 on these trades: %+.0f (fall %.0f%%)' % (ef - 100000, 100 * df))
