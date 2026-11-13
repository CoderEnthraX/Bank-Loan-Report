"""v4.5 study round 1 (asked 2026-11-13): Crooks E (the user's rule) and candidate loss-recovery rules that take less risk in a long losing streak,
on the 19 profitable gold strategies of crooks_user.py (no partial close), $50 base, $10,000 start, no hard cap, gold 2021-2026.
Every rule is Crooks C plus one change (several can be combined):
  wait='min'   Crooks E: while a loss is owed, every trade that is not the recovery trade is the minimum lot (0.01 lot = 1 oz of gold:
               its $ risk is 1 oz x (stop distance + cost), whatever the stop)
  capK         a recovery trade risks at most K x base; the rest of the loss is won back after the next wins (C keeps the leftover)
  halve        each losing recovery trade in a row halves what the next recovery trade goes for (the rest stays owed); a winning recovery
               trade or a new cycle goes back to the whole loss
  brake        every trade's risk x (1 - drawdown / brake), drawdown = equity peak - equity, at least the minimum lot
  wins2        the recovery trade comes only after 2 wins in a row
  owedX        the loss owed is never more than X x base (the excess is forgotten)
  step         each loss in a row halves the next waiting trade (base, 1/2, 1/4 ... at least the minimum lot); a win restores it
  eqpct        the base is this % of equity (the recovery trade as Crooks C)
Random orders: the trade results (R, cost, stop) are shuffled over the real trade times, 200 orders. Output: crooks_e.pkl + crooks_e.txt."""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks, greedy

UNITS_MIN = 1.0          # 0.01 lot x 100 oz


def sim(seq, exitR, wait='base', capK=0.0, halve=False, brake=0.0, wins2=False, owedX=0.0, step=False, eqpct=0.0, base0=50.0, start=10000.0):
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; maxLoss = 0.0; maxRisk = 0.0; ruined = False
    crL = 0.0; winsRow = 0; lossRow = 0; fails = 0; nrec = nrecL = 0; sumRisk = 0.0
    for t, res, c, sd in seq:
        base = eq * eqpct / 100.0 if eqpct > 0 else base0
        rmin = UNITS_MIN * sd * (1.0 + c)                                   # the $ risk of the minimum lot on this trade
        rec = crL > 0 and winsRow >= (2 if wins2 else 1)
        if rec:
            goal = crL * (0.5 ** fails if halve else 1.0)
            r = max(base, goal / exitR)
            if capK > 0: r = min(r, capK * base)
        elif crL > 0 and wait == 'min': r = min(base, rmin)              # 0.01 lot, or the normal size if that is smaller
        elif crL > 0 and step: r = max(rmin, base * 0.5 ** lossRow)
        else: r = base
        if brake > 0: r = max(rmin, r * max(0.0, 1.0 - (peak - eq) / brake))
        pnl = r * (res - c) / (1.0 + c)
        sumRisk += r; maxRisk = max(maxRisk, r)
        if rec: nrec += 1; nrecL += pnl <= 0
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if owedX > 0: crL = min(crL, owedX * base0)
        if crL < 0.01: crL = 0.0; fails = 0
        elif rec: fails = 0 if win else fails + 1
        winsRow = winsRow + 1 if win else 0
        lossRow = 0 if win else lossRow + 1
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, maxRisk=maxRisk, ruined=ruined, nrec=nrec, nrecL=nrecL)


WAYS = [('Crooks C (as now)', {}), ('Off (always $50)', dict(off=True)),
        ('Crooks E: 0.01 lot while waiting', dict(wait='min'))]
for k in (2, 3, 5):
    WAYS.append(('C + recovery at most %dx base' % k, dict(capK=k)))
    WAYS.append(('E + recovery at most %dx base' % k, dict(wait='min', capK=k)))
WAYS += [('C + halve after a lost recovery', dict(halve=True)), ('E + halve after a lost recovery', dict(wait='min', halve=True))]
for b in (10, 20, 40):
    WAYS.append(('C + drawdown brake %dx base' % b, dict(brake=b * 50.0)))
    WAYS.append(('E + drawdown brake %dx base' % b, dict(wait='min', brake=b * 50.0)))
WAYS += [('C + recovery after 2 wins in a row', dict(wins2=True)), ('E + recovery after 2 wins in a row', dict(wait='min', wins2=True))]
for x in (6, 10, 20):
    WAYS.append(('C + owed loss at most %dx base' % x, dict(owedX=x)))
    WAYS.append(('E + owed loss at most %dx base' % x, dict(wait='min', owedX=x)))
WAYS += [('C + halve each waiting trade in a losing run', dict(step=True)),
         ('C + base 0.5% of equity', dict(eqpct=0.5)), ('E + base 0.5% of equity', dict(wait='min', eqpct=0.5)),
         ('E + cap 3x + halve', dict(wait='min', capK=3, halve=True)), ('E + cap 3x + brake 20x', dict(wait='min', capK=3, brake=1000.0)),
         ('E + halve + brake 20x', dict(wait='min', halve=True, brake=1000.0))]


def run(seq, xr, kw):
    if kw.get('off'):
        r = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Off', exitR=xr)
        return dict(net=r['net'], maxDD=r['maxDD'], maxDDpct=r['maxDDpct'], maxLoss=50.0, maxRisk=50.0, ruined=r['ruined'], nrec=0, nrecL=0)
    return sim(seq, xr, **kw)


if __name__ == '__main__':
    rows = {nm: [] for nm, _ in WAYS}; names = []
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            dd = dict(greedy.defaults()); dd.update(d['cfg'])
            if dd['exitAt'] > 1 and dd['p1']: continue                         # partial closes: not in this study (as crooks_user.py)
            seq = [(x[0], x[1], x[4] / x[5], x[5]) for x in sorted(d['trades'], key=lambda x: x[0])]
            xr = crooks.exit_r(d['cfg'])
            if RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Off', exitR=xr)['net'] <= 0: continue
            a = sim(seq, xr)['net']; b = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Crooks C', exitR=xr)['net']
            assert abs(a - b) <= 1e-6 * max(1, abs(b)), (tf, i, a, b)          # plain Crooks C equals the parity-checked simulator
            names.append('%s %s' % (tf, d['name']))
            rng = random.Random(311 + i + 31 * crooks.TFS.index(tf)); times = [t for t, _, _, _ in seq]; outs = [x[1:] for x in seq]
            orders = []
            for _ in range(200):
                q = list(outs); rng.shuffle(q); orders.append([(t,) + o for t, o in zip(times, q)])
            A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            for nm, kw in WAYS:
                r = run(seq, xr, kw); ra = run(A, xr, kw); rb = run(B, xr, kw)
                sims = [run(q, xr, kw) for q in orders]
                rows[nm].append(dict(all=r, both=ra['net'] > 0 and rb['net'] > 0, ruin=sum(z['ruined'] for z in sims) / len(sims),
                                     med=sorted(z['net'] for z in sims)[100], dd95=sorted(z['maxDDpct'] for z in sims)[189],
                                     risk95=sorted(z['maxRisk'] for z in sims)[189], n=len(seq)))
    pickle.dump(dict(rows=rows, names=names), open(S + '/gold/crooks_e1.pkl', 'wb'))
    L = ['%d strategies: %s' % (len(names), '; '.join(names)), '']
    for nm, _ in WAYS:
        rs = rows[nm]
        L.append('%-46s total %+9.0f | fall avg %5.1f%% worst %5.1f%% | biggest trade risk avg $%6.0f max $%7.0f | rec lost %4.1f%% | both halves + %2d/%d | blown %d | random: median %+9.0f, blown %5.1f%%, 95%% fall %5.1f%%, 95%% biggest risk $%7.0f' % (
            nm, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
            sum(r['all']['maxRisk'] for r in rs) / len(rs), max(r['all']['maxRisk'] for r in rs),
            100 * sum(r['all']['nrecL'] for r in rs) / max(1, sum(r['all']['nrec'] for r in rs)), sum(r['both'] for r in rs), len(rs),
            sum(r['all']['ruined'] for r in rs), sum(r['med'] for r in rs), 100 * sum(r['ruin'] for r in rs) / len(rs),
            100 * sum(r['dd95'] for r in rs) / len(rs), sum(r['risk95'] for r in rs) / len(rs)))
    open(S + '/gold/crooks_e1.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
