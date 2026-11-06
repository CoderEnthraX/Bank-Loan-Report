"""Crooks C only, NO hard cap: every way of changing the recovery rule against single wins (L L W L W L W ...), on the 19 gold strategies of
crooks_alt.py (profitable at fixed $50, no partial close), $50 base, $10,000 start. The same measures for every way, 200 random orders each.
(No leverage limit in this simulation: in TradingView / the EA the 1:100 leverage limit can still cut a very big recovery trade.)
Output: crooks_alt3.pkl + crooks_alt3.txt."""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
def sim(seq, exitR, base=50.0, start=10000.0, K=0, frac=1.0, cN=1, W=1, adapt=False, day=False, day1=False, same=False):
    """Crooks C, no cap. K: forget the loss after K losing recovery trades in a row (0 = never). frac: share of the loss a recovery trade goes for
    (the rest is forgotten when it wins). cN: win it back over N wins. W: wins in a row needed before a recovery trade. adapt: 1 win, but 2 in a row
    after a losing recovery trade. day: only on the day of the win. day1: at most one recovery trade a day. same: only in the direction of the win."""
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; maxLoss = 0.0; ruined = False; maxRisk = 0.0
    crL = 0.0; crP = cN; wins = 0; fails = 0; need = W; nrec = nrecL = 0; lastDir = 0; lastDay = None; recDay = None
    for t, res, c, d in seq:
        rec = crL > 0 and wins >= need
        if rec and day: rec = t.date() == lastDay
        if rec and day1: rec = t.date() != recDay
        if rec and same: rec = d == lastDir
        amt = crL / crP * frac
        r = max(base, amt / exitR) if rec else base
        pnl = r * (res - c) / (1.0 + c); maxRisk = max(maxRisk, r)
        if rec: nrec += 1; nrecL += pnl <= 0; recDay = t.date()
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0; crP = cN; fails = 0; need = W
        else:
            crP = cN if not win else (max(1, crP - 1) if rec else crP)
            if rec and not win:
                fails += 1
                if adapt: need = 2
                if K and fails >= K: crL = 0.0; crP = cN; fails = 0; need = W
            elif rec and win:
                fails = 0
                if frac < 1.0 and crP == cN: crL = 0.0; need = W
        wins = wins + 1 if win else 0
        if win: lastDir = d; lastDay = t.date()
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, ruined=ruined, nrec=nrec, nrecL=nrecL, maxRisk=maxRisk)
WAYS = [('Crooks C as now', dict()),
        ('Win it back over 2 wins (setting exists)', dict(cN=2)),
        ('Win it back over 3 wins (setting exists)', dict(cN=3)),
        ('Wait for 2 wins in a row', dict(W=2)),
        ('2 wins in a row only after a lost recovery', dict(adapt=True)),
        ('Recovery only on the day of the win', dict(day=True)),
        ('At most one recovery trade a day', dict(day1=True)),
        ('Recovery only in the direction of the win', dict(same=True)),
        ('Go for 75% of the loss, forget the rest on a win', dict(frac=0.75)),
        ('Go for 50% of the loss, forget the rest on a win', dict(frac=0.5)),
        ('Forget the loss after 1 lost recovery trade', dict(K=1)),
        ('Forget the loss after 2 lost recovery trades', dict(K=2)),
        ('Forget the loss after 3 lost recovery trades', dict(K=3)),
        ('50% of the loss + forget after 2', dict(frac=0.5, K=2)),
        ('Over 2 wins + forget after 2', dict(cN=2, K=2)),
        ('Over 2 wins + forget after 3', dict(cN=2, K=3))]
if __name__ == '__main__':
    rows = {nm: [] for nm, _ in WAYS}; offs = []
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq0 = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
            if any(p for _, _, _, p in seq0): continue
            dirs = {x[0]: x[7] for x in d['trades']}
            seq = [(t, r_, c, dirs[t]) for t, r_, c, p in seq0]
            off = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Off', exitR=xr)
            if off['net'] <= 0: continue
            offs.append(off)
            for kw, cn in ((dict(), 1), (dict(cN=2), 2), (dict(cN=3), 3)):         # the existing rules equal the parity-checked simulator
                a = sim(seq, xr, **kw)['net']; b = RC.simulate([(r_, c) for _, r_, c, _ in seq], 'Crooks C', exitR=xr, cN=cn)['net']
                assert abs(a - b) <= 1e-6 * max(1, abs(b)), (tf, i, cn, a, b)
            rng = random.Random(101 + i + 31 * crooks.TFS.index(tf)); orders = [rng.sample(seq, len(seq)) for _ in range(200)]
            A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            for nm, kw in WAYS:
                r = sim(seq, xr, **kw); ra = sim(A, xr, **kw); rb = sim(B, xr, **kw)
                sims = [sim(q, xr, **kw) for q in orders]
                rows[nm].append(dict(all=r, both=ra['net'] > 0 and rb['net'] > 0, ruin=sum(z['ruined'] for z in sims) / len(sims),
                                     med=sorted(z['net'] for z in sims)[100], dd95=sorted(z['maxDDpct'] for z in sims)[189]))
    pickle.dump(dict(rows=rows, offs=offs), open(S + '/gold/crooks_alt3.pkl', 'wb'))
    L = ['%d strategies; fixed $50 for reference: total %+.0f, average fall %.1f%%, worst fall %.0f%%' % (len(offs), sum(o['net'] for o in offs),
         100 * sum(o['maxDDpct'] for o in offs) / len(offs), 100 * max(o['maxDDpct'] for o in offs))]
    for nm, _ in WAYS:
        rs = rows[nm]
        L.append('%-50s total %+9.0f | avg fall %5.1f%% worst %4.0f%% | biggest single loss avg $%5.0f max $%6.0f | recovery trades lost %4.1f%% | both halves + %2d/%d | blown (actual order) %d | random orders: median total %+9.0f, blown %5.1f%%, 95%% fall %5.1f%%' % (
            nm, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
            sum(r['all']['maxLoss'] for r in rs) / len(rs), max(r['all']['maxLoss'] for r in rs), 100 * sum(r['all']['nrecL'] for r in rs) / max(1, sum(r['all']['nrec'] for r in rs)),
            sum(r['both'] for r in rs), len(rs), sum(r['all']['ruined'] for r in rs), sum(r['med'] for r in rs), 100 * sum(r['ruin'] for r in rs) / len(rs),
            100 * sum(r['dd95'] for r in rs) / len(rs)))
    open(S + '/gold/crooks_alt3.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
