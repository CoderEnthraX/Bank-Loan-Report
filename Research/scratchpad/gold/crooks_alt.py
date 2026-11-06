"""Crooks C when wins come one at a time (L L W L L W L W ...): the recovery trade (the trade right after a win) then loses big again and again.
Ways to avoid it, tested on gold 2021-2026 on every catalogue strategy that is profitable at fixed $50 (as crooks_cn.py), $50 base:
  C        Crooks C as now (recovery trade = the trade right after a win while a loss is owed)
  C/2      Crooks C over 2 wins (existing setting: half, then the rest)
  2W       recovery trade only after 2 wins in a row
  adapt    the first recovery after 1 win; after a losing recovery trade the next one waits for 2 wins in a row
  fail1    forget the loss (start again at the base) after 1 losing recovery trade;   fail2: after 2 losing recovery trades in a row
  dir      recovery only if the trade after the win goes the same way as the win (else that trade risks the base)
  day      recovery only on the same day as the win;     day1: at most one recovery trade per day
  half     the recovery trade wins back half of the loss, the rest is forgotten
plus Off (fixed $50) and Paroli as references. Each with $500 cap + Start again, $500 Clamp and no cap; each half; 200 random orders.
Also: are wins clustered? P(win | previous win) vs P(win | previous loss) on the same trades.
Output: crooks_alt.pkl + crooks_alt.txt."""
import sys, pickle, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
VARS = ['off', 'C', 'C/2', '2W', 'adapt', 'fail1', 'fail2', 'dir', 'day', 'day1', 'half']
def sim(seq, var, base=50.0, cap=500.0, act='reset', exitR=1.0, start=10000.0):
    """seq: (time, R, cost in R, direction). Crooks C with variant var."""
    cN = 2 if var == 'C/2' else 1
    eq = start; peak = start; maxDD = maxDDp = net = 0.0; n = nrec = nrecL = 0; maxLoss = 0.0; lossRun = worstRun = 0.0; ruined = False
    crL = 0.0; crP = cN; wins = 0; need = 1; fails = 0; lastWinDir = 0; lastWinDay = None; recDay = None; maxRisk = 0.0
    for t, res, c, d in seq:
        owed = crL > 0
        if var == 'off': rec = False
        elif var in ('C', 'C/2', 'fail1', 'fail2', 'half'): rec = owed and wins >= 1
        elif var == '2W': rec = owed and wins >= 2
        elif var == 'adapt': rec = owed and wins >= need
        elif var == 'dir': rec = owed and wins >= 1 and d == lastWinDir
        elif var == 'day': rec = owed and wins >= 1 and t.date() == lastWinDay
        elif var == 'day1': rec = owed and wins >= 1 and t.date() != recDay
        amt = crL / crP * (0.5 if var == 'half' else 1.0)
        r = max(base, amt / exitR) if rec else base
        if cap > 0 and r > cap:
            if act == 'reset': crL = 0.0; crP = cN; fails = 0; need = 1; rec = False; r = min(base, cap)
            else: r = cap
        pnl = r * (res - c) / (1.0 + c); n += 1; maxRisk = max(maxRisk, r)
        if rec:
            nrec += 1; nrecL += pnl <= 0; recDay = t.date()
        eq += pnl; net += pnl; maxLoss = max(maxLoss, -pnl)
        lossRun = lossRun + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, lossRun)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if crL < 0.01: crL = 0.0; crP = cN; fails = 0; need = 1
        else:
            crP = cN if not win else (max(1, crP - 1) if rec else crP)
            if rec and not win:
                fails += 1; need = 2
                if (var == 'fail1' and fails >= 1) or (var == 'fail2' and fails >= 2): crL = 0.0; crP = cN; fails = 0; need = 1
            elif rec and win:
                fails = 0
                if var == 'half': crL = 0.0; crP = cN; need = 1      # half won back, the other half is forgotten
        wins = wins + 1 if win else 0
        if win: lastWinDir = d; lastWinDay = t.date()
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, maxLoss=maxLoss, worstRun=-worstRun, ruined=ruined, n=n, nrec=nrec, nrecL=nrecL, maxRisk=maxRisk)
def main():
    out = {}; corr = dict(w=0, n=0, ww=0, nw=0, wl=0, nl=0, www=0, nww=0, wlw=0, nlw=0, recW=0, recN=0)
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq0 = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
            dirs = {x[0]: x[7] for x in d['trades']}
            seq = [(t, res, c, dirs[t]) for t, res, c, parts in seq0]
            if any(p for _, _, _, p in seq0): continue                         # settings with a partial close at TP1 are left out (rare)
            off = RC.simulate([(res, c) for _, res, c, _ in seq], 'Off', exitR=xr)
            if off['net'] <= 0: continue
            # check: variant C equals the existing simulator (strategy / EA parity-checked)
            for cap, act in ((500.0, 'reset'), (500.0, 'clamp'), (0.0, 'clamp')):
                a = sim(seq, 'C', cap=cap, act=act, exitR=xr)['net']; b = RC.simulate([(res, c) for _, res, c, _ in seq], 'Crooks C', cap=cap, capAction=act, exitR=xr)['net']
                assert abs(a - b) <= 1e-6 * max(1.0, abs(b)), (tf, i, cap, act, a, b)
                a = sim(seq, 'C/2', cap=cap, act=act, exitR=xr)['net']; b = RC.simulate([(res, c) for _, res, c, _ in seq], 'Crooks C', cap=cap, capAction=act, exitR=xr, cN=2)['net']
                assert abs(a - b) <= 1e-6 * max(1.0, abs(b)), (tf, i, cap, act, 'C/2', a, b)
            # win clustering
            W = [((res - c) / (1 + c)) > 0 for _, res, c, _ in seq]
            for k in range(1, len(W)):
                corr['n'] += 1; corr['w'] += W[k]
                if W[k - 1]: corr['nw'] += 1; corr['ww'] += W[k]
                else: corr['nl'] += 1; corr['wl'] += W[k]
                if k >= 2 and W[k - 1] and W[k - 2]: corr['nww'] += 1; corr['www'] += W[k]
                if k >= 2 and W[k - 1] and not W[k - 2]: corr['nlw'] += 1; corr['wlw'] += W[k]
            A = [x for x in seq if x[0].year <= 2023]; B = [x for x in seq if x[0].year >= 2024]
            rng = random.Random(17 + i + 31 * crooks.TFS.index(tf)); orders = []
            for _ in range(200):
                q = list(seq); rng.shuffle(q); orders.append(q)
            row = {}
            for v in VARS:
                for cap, act in ((500.0, 'reset'), (500.0, 'clamp'), (0.0, 'clamp')):
                    kw = dict(cap=cap, act=act, exitR=xr)
                    r = dict(all=sim(seq, v, **kw), A=sim(A, v, **kw), B=sim(B, v, **kw))
                    if (cap, act) == (500.0, 'reset'):
                        sims = [sim(q, v, **kw) for q in orders]
                        nets = sorted(z['net'] for z in sims); dds = sorted(z['maxDDpct'] for z in sims); ml = sorted(z['worstRun'] for z in sims)
                        r['med'] = nets[len(nets) // 2]; r['p5'] = nets[int(0.05 * len(nets))]; r['dd95'] = dds[int(0.95 * len(dds))]; r['run95'] = ml[int(0.95 * len(ml))]
                    if cap == 0:
                        r['ruin'] = sum(1 for q in orders[:100] if sim(q, v, **kw)['ruined']) / 100.0
                    row[(v, cap, act)] = r
            par = RC.simulate([(res, c) for _, res, c, _ in seq], RC.MODES[13], exitR=xr)
            assert abs(sim(seq, 'off', exitR=xr)['net'] - off['net']) <= 1e-6 * max(1.0, abs(off['net']))
            out[(tf, i)] = dict(name=d['name'], off=off, rows=row, paroli=par, n=len(seq), exitR=xr)
    pickle.dump(dict(out=out, corr=corr), open(S + '/gold/crooks_alt.pkl', 'wb'))
    L = []
    c = corr
    L.append('Win clustering over the %d strategies (%d trades): P(win) %.1f%% | after a win %.1f%% | after a loss %.1f%% | after 2 wins %.1f%% | after loss-then-win %.1f%%' % (
        len(out), c['n'], 100 * c['w'] / c['n'], 100 * c['ww'] / c['nw'], 100 * c['wl'] / c['nl'], 100 * c['www'] / c['nww'], 100 * c['wlw'] / c['nlw']))
    for cap, act, nm in ((500.0, 'reset', '$500 cap, Start again'), (500.0, 'clamp', '$500 cap, Clamp'), (0.0, 'clamp', 'no cap')):
        L.append('\n%s' % nm)
        for v in VARS:
            rs = [x['rows'][(v, cap, act)] for x in out.values()]
            line = '  %-6s total %+9.0f | avg fall %5.1f%% (worst %3.0f%%) | worst losing run avg $%5.0f (max $%5.0f) | biggest single loss avg $%4.0f | recovery trades %5d, %4.1f%% lost | both halves + on %2d/%d | better net than C on %2d' % (
                v, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
                sum(r['all']['worstRun'] for r in rs) / len(rs), max(r['all']['worstRun'] for r in rs), sum(r['all']['maxLoss'] for r in rs) / len(rs),
                sum(r['all']['nrec'] for r in rs), 100 * sum(r['all']['nrecL'] for r in rs) / max(1, sum(r['all']['nrec'] for r in rs)),
                sum(1 for r in rs if r['A']['net'] > 0 and r['B']['net'] > 0), len(rs),
                sum(1 for x in out.values() if x['rows'][(v, cap, act)]['all']['net'] > x['rows'][('C', cap, act)]['all']['net']))
            if 'med' in rs[0]: line += ' | random orders: median total %+8.0f, 95%% fall avg %4.1f%%, 95%% losing run avg $%5.0f' % (sum(r['med'] for r in rs), 100 * sum(r['dd95'] for r in rs) / len(rs), sum(r['run95'] for r in rs) / len(rs))
            if 'ruin' in rs[0]: line += ' | blown in %4.1f%% of random orders (avg)' % (100 * sum(r['ruin'] for r in rs) / len(rs))
            L.append(line)
    L.append('\nParoli (reference): total %+.0f, avg fall %.1f%%' % (sum(x['paroli']['net'] for x in out.values()), 100 * sum(x['paroli']['maxDDpct'] for x in out.values()) / len(out)))
    open(S + '/gold/crooks_alt.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
if __name__ == '__main__':
    main()
