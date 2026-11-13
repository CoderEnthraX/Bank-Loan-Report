"""v4.5 study round 2: Crooks E with the waiting trades at 0.01 lot or the normal size if that is smaller, and the recovery-size limits that
round 1 (crooks_e_round1_rawmin.txt) showed to work, in more forms. Same 19 gold strategies, $50 base, $10,000 start, no hard cap, 200 random
orders. Every rule is Crooks C plus one change (some combined):
  wait='min'  Crooks E: while a loss is owed, the trades that are not the recovery trade are 0.01 lot (1 oz), or the normal size if smaller
  capK        a recovery trade risks at most K x base (the rest is won back after the next wins: C keeps the leftover)
  owedX       the loss owed is at most X x base (the excess is accepted as lost)
  capEq       a recovery trade risks at most this % of the equity (closed trades)
  recBrake    the recovery trade's size shrinks with the drawdown: x (1 - drawdown / recBrake), at least the base (base trades unchanged)
  house       a recovery trade risks at most base + this share of the profit made so far (closed): no profit, no recovery
  decay       each losing recovery trade in a row halves the most the next one may risk (first one: as Crooks C)
  forgetN     the loss is forgotten after N losing recovery trades in a row (the existing Crooks C rule 'forget', for comparison)"""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks, greedy

UNITS_MIN = 1.0          # 0.01 lot x 100 oz


def sim(seq, exitR, wait='base', capK=0.0, owedX=0.0, capEq=0.0, recBrake=0.0, house=0.0, decay=False, forgetN=0, base=50.0, start=10000.0):
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; maxLoss = 0.0; maxRisk = 0.0; ruined = False
    crL = 0.0; winsRow = 0; fails = 0; firstRec = 0.0; nrec = nrecL = 0; worstRun = 0.0; run = 0.0
    for t, res, c, sd in seq:
        rmin = UNITS_MIN * sd * (1.0 + c)
        rec = crL > 0 and winsRow >= 1
        if rec:
            r = max(base, crL / exitR)
            if capK > 0: r = min(r, capK * base)
            if capEq > 0: r = min(r, max(base, eq * capEq / 100.0))
            if recBrake > 0: r = max(base, r * max(0.0, 1.0 - (peak - eq) / recBrake))
            if house > 0: r = min(r, base + house * max(0.0, net))
            if decay:
                if fails == 0: firstRec = r
                else: r = max(base, min(r, firstRec * 0.5 ** fails))
        elif crL > 0 and wait == 'min': r = min(base, rmin)
        else: r = base
        pnl = r * (res - c) / (1.0 + c)
        maxRisk = max(maxRisk, r)
        if rec: nrec += 1; nrecL += pnl <= 0
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        run = run + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, run)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if owedX > 0: crL = min(crL, owedX * base)
        if crL < 0.01: crL = 0.0; fails = 0
        elif rec:
            fails = 0 if win else fails + 1
            if forgetN and fails >= forgetN: crL = 0.0; fails = 0
        winsRow = winsRow + 1 if win else 0
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, maxRisk=maxRisk, ruined=ruined, nrec=nrec, nrecL=nrecL, worstRun=-worstRun)


WAYS = [('Crooks C (as now)', {}), ('Off (always $50)', dict(off=True)), ('Crooks E: 0.01 lot while waiting', dict(wait='min'))]
for k in (2, 3, 4, 5): WAYS.append(('C + recovery at most %dx base' % k, dict(capK=k)))
for x in (6, 10, 15, 20): WAYS.append(('C + owed loss at most %dx base' % x, dict(owedX=x)))
for p in (1.0, 1.5, 2.0, 3.0): WAYS.append(('C + recovery at most %.1f%% of equity' % p, dict(capEq=p)))
for b in (20, 40, 80): WAYS.append(('C + recovery shrinks in drawdown %dx base' % b, dict(recBrake=b * 50.0)))
for h in (0.10, 0.25, 0.50): WAYS.append(('C + recovery at most base + %d%% of profit' % (100 * h), dict(house=h)))
WAYS += [('C + each lost recovery halves the next', dict(decay=True)), ('C + forget after 2 lost recoveries', dict(forgetN=2)),
         ('C + forget after 3 lost recoveries', dict(forgetN=3)),
         ('E + recovery at most 3x base', dict(wait='min', capK=3)), ('E + owed loss at most 10x base', dict(wait='min', owedX=10)),
         ('E + recovery at most 2% of equity', dict(wait='min', capEq=2.0)), ('E + each lost recovery halves the next', dict(wait='min', decay=True)),
         ('C + cap 3x + owed 10x', dict(capK=3, owedX=10)), ('C + cap 3x + 2% of equity', dict(capK=3, capEq=2.0)),
         ('C + decay + cap 5x', dict(decay=True, capK=5)), ('C + decay + owed 20x', dict(decay=True, owedX=20))]


def run(seq, xr, kw):
    if kw.get('off'):
        r = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Off', exitR=xr)
        return dict(net=r['net'], maxDD=r['maxDD'], maxDDpct=r['maxDDpct'], maxLoss=50.0, maxRisk=50.0, ruined=r['ruined'], nrec=0, nrecL=0, worstRun=r['worstRun'])
    return sim(seq, xr, **kw)


if __name__ == '__main__':
    rows = {nm: [] for nm, _ in WAYS}; names = []
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            dd = dict(greedy.defaults()); dd.update(d['cfg'])
            if dd['exitAt'] > 1 and dd['p1']: continue
            seq = [(x[0], x[1], x[4] / x[5], x[5]) for x in sorted(d['trades'], key=lambda x: x[0])]
            xr = crooks.exit_r(d['cfg'])
            if RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Off', exitR=xr)['net'] <= 0: continue
            a = sim(seq, xr)['net']; b = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Crooks C', exitR=xr)['net']
            assert abs(a - b) <= 1e-6 * max(1, abs(b)), (tf, i, a, b)
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
                                     risk95=sorted(z['maxRisk'] for z in sims)[189], run95=sorted(z['worstRun'] for z in sims)[189], n=len(seq)))
    pickle.dump(dict(rows=rows, names=names), open(S + '/gold/crooks_e2.pkl', 'wb'))
    L = ['%d strategies: %s' % (len(names), '; '.join(names)), '']
    for nm, _ in WAYS:
        rs = rows[nm]
        L.append('%-44s total %+9.0f | fall avg %5.1f%% worst %5.1f%% | worst losing run avg $%6.0f | biggest risk max $%6.0f | both + %2d/%d | blown %d | random: median %+9.0f, blown %5.1f%%, 95%% fall %5.1f%%, 95%% losing run $%6.0f' % (
            nm, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
            sum(r['all']['worstRun'] for r in rs) / len(rs), max(r['all']['maxRisk'] for r in rs), sum(r['both'] for r in rs), len(rs),
            sum(r['all']['ruined'] for r in rs), sum(r['med'] for r in rs), 100 * sum(r['ruin'] for r in rs) / len(rs),
            100 * sum(r['dd95'] for r in rs) / len(rs), sum(r['run95'] for r in rs) / len(rs)))
    open(S + '/gold/crooks_e2.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
