"""Crooks C, single wins (follow-up of crooks_alt.py): forget the loss after K losing recovery trades in a row, a recovery trade that goes for only
part of the loss (the rest forgotten when it wins), their mix, over 2 wins + forget, and smaller hard caps ($250 / $150 Start again), on the 19 gold
strategies of crooks_alt.py (profitable at fixed $50, no partial close). 100 random orders each. Output: crooks_alt2.pkl + crooks_alt2.txt."""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
def sim(seq, base=50.0, cap=500.0, act='reset', exitR=1.0, start=10000.0, K=0, frac=1.0, cN=1):
    """Crooks C; K = forget the loss after K losing recovery trades in a row (0 = never); frac = share of the loss a recovery trade goes for
    (the rest is forgotten when it wins); cN = over N wins"""
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; maxLoss = 0.0; lossRun = worstRun = 0.0; ruined = False
    crL = 0.0; crP = cN; wins = 0; fails = 0; nrec = nrecL = 0
    for t, res, c in seq:
        rec = crL > 0 and wins >= 1
        amt = crL / crP * frac
        r = max(base, amt / exitR) if rec else base
        if cap > 0 and r > cap:
            if act == 'reset': crL = 0.0; crP = cN; fails = 0; rec = False; r = min(base, cap)
            else: r = cap
        pnl = r * (res - c) / (1.0 + c)
        if rec: nrec += 1; nrecL += pnl <= 0
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        lossRun = lossRun + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, lossRun)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0; crP = cN; fails = 0
        else:
            crP = cN if not win else (max(1, crP - 1) if rec else crP)
            if rec and not win:
                fails += 1
                if K and fails >= K: crL = 0.0; crP = cN; fails = 0
            elif rec and win:
                fails = 0
                if frac < 1.0 and crP == cN: crL = 0.0          # the part went for is back, the rest is forgotten
        wins = wins + 1 if win else 0
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, worstRun=-worstRun, ruined=ruined, nrec=nrec, nrecL=nrecL)
V = [('C (now)', dict(K=0)), ('forget after 1 lost recovery', dict(K=1)), ('forget after 2 lost recoveries', dict(K=2)), ('forget after 3', dict(K=3)),
     ('win back 50%', dict(K=0, frac=0.5)), ('win back 50% + forget after 2', dict(K=2, frac=0.5)), ('over 2 wins + forget after 2', dict(K=2, cN=2)),
     ('win back 75%', dict(K=0, frac=0.75))]
if __name__ == '__main__':
    res = {}
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq0 = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
            if any(p for _, _, _, p in seq0): continue
            seq = [(t, r_, c) for t, r_, c, p in seq0]
            if RC.simulate([(r_, c) for _, r_, c in seq], 'Off', exitR=xr)['net'] <= 0: continue
            for cap, act in ((500.0, 'reset'), (0.0, 'clamp')):                # the plain rule equals the parity-checked simulator
                a = sim(seq, cap=cap, act=act, exitR=xr)['net']; b = RC.simulate([(r_, c) for _, r_, c in seq], 'Crooks C', cap=cap, capAction=act, exitR=xr)['net']
                assert abs(a - b) <= 1e-6 * max(1, abs(b))
            rng = random.Random(3 + i + 31 * crooks.TFS.index(tf)); orders = [rng.sample(seq, len(seq)) for _ in range(100)]
            A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            for nm, kw in V:
                for cap, act in ((500.0, 'reset'), (250.0, 'reset'), (150.0, 'reset'), (500.0, 'clamp'), (0.0, 'clamp')):
                    if nm != 'C (now)' and cap in (250.0, 150.0): continue
                    r = sim(seq, cap=cap, act=act, exitR=xr, **kw)
                    ra = sim(A, cap=cap, act=act, exitR=xr, **kw); rb = sim(B, cap=cap, act=act, exitR=xr, **kw)
                    sims = [sim(q, cap=cap, act=act, exitR=xr, **kw) for q in orders]
                    res.setdefault((nm, cap, act), []).append(dict(all=r, both=ra['net'] > 0 and rb['net'] > 0, ruin=sum(z['ruined'] for z in sims) / len(sims),
                                                                  dd95=sorted(z['maxDDpct'] for z in sims)[94], med=sorted(z['net'] for z in sims)[50]))
    L = []
    for (nm, cap, act), rs in res.items():
        L.append('%-32s %-16s total %+8.0f | avg fall %5.1f%% worst %4.0f%% | biggest single loss avg $%5.0f | recovery lost %4.1f%% | both halves + %2d/%d | random: median %+8.0f, 95%% fall %4.1f%%, blown %4.1f%%' % (
            nm, ('no cap' if cap == 0 else '$%d %s' % (cap, 'start again' if act == 'reset' else 'clamp')), sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs),
            100 * max(r['all']['maxDDpct'] for r in rs), sum(r['all']['maxLoss'] for r in rs) / len(rs), 100 * sum(r['all']['nrecL'] for r in rs) / max(1, sum(r['all']['nrec'] for r in rs)),
            sum(r['both'] for r in rs), len(rs), sum(r['med'] for r in rs), 100 * sum(r['dd95'] for r in rs) / len(rs), 100 * sum(r['ruin'] for r in rs) / len(rs)))
    pickle.dump(res, open(S + '/gold/crooks_alt2.pkl', 'wb'))
    open(S + '/gold/crooks_alt2.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
