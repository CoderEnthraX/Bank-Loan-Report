"""The user's two Crooks C rules (asked 2026-11-06), no hard cap, on the 19 gold strategies of crooks_alt.py, $50 base, $10,000 start:
  wait   after N losing recovery trades in a row: no recovery trade until M wins in a row (all trades at the base meanwhile, the loss is kept);
         A1: the trade right after the M-th win is the recovery trade;  A2: after the M wins the first recovery trade needs a loss, then a win
  skip   after N losing recovery trades in a row: no trades for the rest of that day and D more trading days (Mon-Fri; none of the 19 has a day
         filter); B1: the loss is kept;  B2: the loss is forgotten
plus Crooks C as now, forget after N and 50% + forget after N for comparison. "Losing recovery trades in a row": recovery trades that lost with
no winning recovery trade between them (base trades between them do not break the count). Random orders: the trade results are shuffled over
the real trade times (so the day rules still see real dates), 200 orders. Output: crooks_user.pkl + crooks_user.txt."""
import sys, pickle, random, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
def end_day(d0, D, all_days=False):
    """last day of a pause: D counted days after day d0 (counted: Mon-Fri, or every day)"""
    d = d0; left = D
    while left > 0:
        d += datetime.timedelta(days=1)
        if all_days or d.weekday() < 5: left -= 1
    return d
def sim(seq, exitR, rule='C', N=2, M=2, D=3, frac=1.0, base=50.0, start=10000.0):
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; maxLoss = 0.0; ruined = False
    crL = 0.0; wins = 0; fails = 0; nrec = nrecL = 0; skipped = 0
    waiting = False; wW = 0; armed = True; pauseEnd = None
    for t, res, c in seq:
        if pauseEnd is not None:
            if t.date() <= pauseEnd: skipped += 1; continue
            pauseEnd = None
        rec = crL > 0 and wins >= 1 and not waiting and armed
        r = max(base, crL * frac / exitR) if rec else base
        pnl = r * (res - c) / (1.0 + c)
        if rec: nrec += 1; nrecL += pnl <= 0
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if waiting:
            wW = wW + 1 if win else 0
            if wW >= M:
                waiting = False; wW = 0
                if rule == 'A2': armed = False                    # the first recovery trade after the wait needs a loss, then a win
        if not win and not armed: armed = True
        if crL < 0.01:
            crL = 0.0; fails = 0; waiting = False; wW = 0; armed = True
        elif rec and win:
            fails = 0
            if frac < 1.0: crL = 0.0                               # the part went for is back, the rest is forgotten
        elif rec and not win:
            fails += 1
            if fails >= N:
                fails = 0
                if rule in ('A1', 'A2'): waiting = True; wW = 0
                elif rule in ('B1', 'B2'):
                    pauseEnd = end_day(t.date(), D)
                    if rule == 'B2': crL = 0.0
                elif rule in ('forget', 'half'): crL = 0.0
        wins = wins + 1 if win else 0
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, ruined=ruined, nrec=nrec, nrecL=nrecL, skipped=skipped)
WAYS = [('Crooks C as now', dict(rule='C', N=99))]
for N in (2, 3):
    for M in (2, 3):
        WAYS.append(('Wait for %d wins after %d lost recoveries, recovery right after the wins' % (M, N), dict(rule='A1', N=N, M=M)))
        WAYS.append(('Wait for %d wins after %d lost recoveries, then a loss + win first' % (M, N), dict(rule='A2', N=N, M=M)))
    for D in (2, 3, 4):
        WAYS.append(('Skip %d trading days after %d lost recoveries, keep the loss' % (D, N), dict(rule='B1', N=N, D=D)))
        WAYS.append(('Skip %d trading days after %d lost recoveries, forget the loss' % (D, N), dict(rule='B2', N=N, D=D)))
    WAYS.append(('Forget the loss after %d lost recoveries' % N, dict(rule='forget', N=N)))
    WAYS.append(('50%% of the loss + forget after %d lost recoveries' % N, dict(rule='half', N=N, frac=0.5)))
if __name__ == '__main__':
    rows = {nm: [] for nm, _ in WAYS}
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq0 = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
            if any(p for _, _, _, p in seq0): continue
            seq = [(t, r_, c) for t, r_, c, p in seq0]
            if RC.simulate([(r_, c) for _, r_, c in seq], 'Off', exitR=xr)['net'] <= 0: continue
            a = sim(seq, xr, rule='C', N=99)['net']; b = RC.simulate([(r_, c) for _, r_, c in seq], 'Crooks C', exitR=xr)['net']
            assert abs(a - b) <= 1e-6 * max(1, abs(b)), (tf, i, a, b)          # the plain rule equals the parity-checked simulator
            rng = random.Random(211 + i + 31 * crooks.TFS.index(tf)); times = [t for t, _, _ in seq]; outs = [(r_, c) for _, r_, c in seq]
            orders = []
            for _ in range(200):
                q = list(outs); rng.shuffle(q); orders.append([(t, r_, c) for t, (r_, c) in zip(times, q)])
            A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            for nm, kw in WAYS:
                r = sim(seq, xr, **kw); ra = sim(A, xr, **kw); rb = sim(B, xr, **kw)
                sims = [sim(q, xr, **kw) for q in orders]
                rows[nm].append(dict(all=r, both=ra['net'] > 0 and rb['net'] > 0, ruin=sum(z['ruined'] for z in sims) / len(sims),
                                     med=sorted(z['net'] for z in sims)[100], dd95=sorted(z['maxDDpct'] for z in sims)[189], n=len(seq)))
    pickle.dump(rows, open(S + '/gold/crooks_user.pkl', 'wb'))
    L = []
    for nm, _ in WAYS:
        rs = rows[nm]
        L.append('%-72s total %+9.0f | avg fall %5.1f%% worst %4.0f%% | biggest loss avg $%5.0f max $%5.0f | rec lost %4.1f%% | trades skipped %4.1f%% | both halves + %2d/%d | blown %d | random: median %+9.0f, blown %5.1f%%, 95%% fall %5.1f%%' % (
            nm, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
            sum(r['all']['maxLoss'] for r in rs) / len(rs), max(r['all']['maxLoss'] for r in rs), 100 * sum(r['all']['nrecL'] for r in rs) / max(1, sum(r['all']['nrec'] for r in rs)),
            100 * sum(r['all']['skipped'] for r in rs) / sum(r['n'] for r in rs), sum(r['both'] for r in rs), len(rs), sum(r['all']['ruined'] for r in rs),
            sum(r['med'] for r in rs), 100 * sum(r['ruin'] for r in rs) / len(rs), 100 * sum(r['dd95'] for r in rs) / len(rs)))
    open(S + '/gold/crooks_user.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
