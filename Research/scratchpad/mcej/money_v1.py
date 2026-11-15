"""Monthly Crooks E-J x profit ladder workbook (asked 2026-11-15): the money runs.
Every rule / level on every strategy's gold trades, two ways:
  cont   ONE account from the first trade (Jan 2021) to the end of the data (2 Oct 2026), as the strategy / EA runs it; each trade's P&L is
         booked in the IST calendar month of its exit. The profit ladder switches on once the account's best closed profit reaches $1,000.
  fresh  each IST calendar month on its own: the trades that START in that month, a fresh $10,000 account and a fresh recovery / ladder state
         on the 1st (as the earlier monthly workbooks).
Money = the reference simulators (gold/recovery.py for the Auction Retest strategy / EA, fractal/recovery_tol.py for the grid), each proven
equal to its Pine strategy / EA by the parity suites. Per trade: (R, cost in R, parts None, day events None, leverage limit, 0.01-lot $ risk).
Settings = the strategies' defaults: $50 base, $10,000 start (per strategy), 1:100 leverage, E / I lot 0.01, F x3, G x10, H 1%, J x20,
ladder target $1,000; hard cap: Auction Retest off (its default), grid $500 Clamp (its default). No lot rounding.
Usage: money.py ars | grid   -> mcej/ars_money.pkl / grid_money.pkl"""
import sys, pickle, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')

LEVELS = ('Off', 'Low', 'Medium', 'High', 'Extra high', 'Max')
RULES = ('Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')
CONFIGS = [('Crooks E', 'Off')] + [(r, l) for r in RULES[1:] for l in LEVELS]


def months():
    out = []; y, m = 2021, 1
    while (y, m) <= (2026, 10):
        out.append('%04d-%02d' % (y, m)); m += 1
        if m == 13: y, m = y + 1, 1
    return out


MONTHS = months()


def mkey(t): return '%04d-%02d' % (t.year, t.month)


def run(RC, trs, rule, lvl, P):
    """one account over trs (dicts with R, c, levk, rmin): per trade (risk, pnl, ladder on before the trade); None after a blown account"""
    tup = [(x['R'], x['c'], None, None, x['levk'], x['rmin']) for x in trs]
    tr = []
    r = RC.simulate(tup, rule, base=P['base'], cap=P['cap'], capAction=P['capAction'], exitR=P['exitR'], start=P['start'], trace=tr,
                    fK=3.0, gX=10.0, hPct=1.0, jX=20.0, lad=None if lvl == 'Off' else lvl, ladT=P['ladT'])
    assert 'SKIP' not in tr
    out = []; net = 0.0; pk = 0.0
    for k, x in enumerate(trs):
        if k >= len(tr): out.append(None); continue
        on = lvl != 'Off' and rule != 'Crooks E' and pk >= P['ladT']
        pnl = tr[k] * (x['R'] - x['c']) / (1.0 + x['c'])
        out.append((tr[k], pnl, on)); net += pnl; pk = max(pk, net)
    assert abs(net - r['net']) <= 1e-6 * max(1.0, abs(r['net'])), (net, r['net'])
    return out, r


def month_stats(rows, start_eq):
    """rows: [(time of exit, risk, pnl, ladder on)] of one month in booking order; start_eq: the balance on the 1st"""
    eq = start_eq; pkm = start_eq; drop = 0.0; gp = gl = 0.0; big = 0.0; mr = 0.0; on = False
    for _, risk, pnl, lon in rows:
        eq += pnl; pkm = max(pkm, eq); drop = max(drop, pkm - eq)
        if pnl > 0: gp += pnl
        else: gl -= pnl; big = max(big, -pnl)
        mr = max(mr, risk); on = on or lon
    return dict(net=eq - start_eq, drop=drop, gp=gp, gl=gl, bigLoss=big, maxRisk=mr, ladOn=on, n=len(rows))


def cont_months(per, trs, start):
    """per: run() output for trs; -> {month: stats} on one account, booked by the exit month; plus whole-period numbers"""
    rows = {m: [] for m in MONTHS}; blown = None
    for x, v in zip(trs, per):
        if v is None:
            if blown is None: blown = mkey(x['tx'])
            continue
        rows[mkey(x['tx'])].append((x['tx'], v[0], v[1], v[2]))
    out = {}; eq = start; pk = start; dd = 0.0; ddp = 0.0; firstOn = None
    for m in MONTHS:
        st = month_stats(rows[m], eq)
        for _, _, pnl, _ in rows[m]:
            eq += pnl; pk = max(pk, eq); dd = max(dd, pk - eq); ddp = max(ddp, (pk - eq) / pk)
        st['end'] = eq; out[m] = st
        if st['ladOn'] and firstOn is None: firstOn = m
    return out, dict(net=eq - start, end=eq, maxDD=dd, maxDDpct=ddp, ladFirst=firstOn, blown=blown)


def combine(acc_list, start_each):
    """the grid: several strategies (each its own account) as one: the summed balance, trades merged by exit time"""
    rows = {m: [] for m in MONTHS}
    for trs, per in acc_list:
        for x, v in zip(trs, per):
            if v is not None: rows[mkey(x['tx'])].append((x['tx'], x['t'], v[0], v[1], v[2]))
    start = start_each * len(acc_list); out = {}; eq = start; pk = start; dd = 0.0; ddp = 0.0
    for m in MONTHS:
        rs = sorted(rows[m], key=lambda z: (z[0], z[1]))
        st = month_stats([(a, r_, p, o) for a, _, r_, p, o in rs], eq)
        for z in rs:
            eq += z[3]; pk = max(pk, eq); dd = max(dd, pk - eq); ddp = max(ddp, (pk - eq) / pk)
        st['end'] = eq; out[m] = st
    return out, dict(net=eq - start, end=eq, maxDD=dd, maxDDpct=ddp)


def fresh_months(RC, trs, rule, lvl, P):
    """each month on its own (trades that start in it, fresh account and state)"""
    by = {m: [] for m in MONTHS}
    for x in trs:
        k = mkey(x['t'])
        if k in by: by[k].append(x)
    out = {}
    for m in MONTHS:
        if not by[m]: out[m] = dict(net=0.0, n=0, drop=0.0, ladOn=False, blown=False); continue
        per, r = run(RC, by[m], rule, lvl, P)
        st = month_stats([(x['tx'], v[0], v[1], v[2]) for x, v in zip(by[m], per) if v is not None], P['start'])
        st['blown'] = r['ruined']; out[m] = st
    return out


def strategy_block(RC, trs, P):
    res = {}
    for rule, lvl in CONFIGS:
        per, r = run(RC, trs, rule, lvl, P)
        cm, whole = cont_months(per, trs, P['start'])
        res[(rule, lvl)] = dict(per=per, cont=cm, whole=whole, fresh=fresh_months(RC, trs, rule, lvl, P), ruined=r['ruined'], maxRisk=r['maxRisk'])
    return res


def trade_counts(trs):
    """per month: trades booked (exit month) / started (entry month), wins, losses (the sign of a trade is the same for every rule)"""
    c = {m: dict(n=0, w=0, l=0, nStart=0) for m in MONTHS}
    for x in trs:
        k = mkey(x['tx'])
        if k in c:
            c[k]['n'] += 1
            if x['R'] - x['c'] > 0: c[k]['w'] += 1
            else: c[k]['l'] += 1
        k2 = mkey(x['t'])
        if k2 in c: c[k2]['nStart'] += 1
    return c


if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'ars':
        import recovery as RC
        D = pickle.load(open(S + '/mcej/ars_trades.pkl', 'rb')); out = {}
        for key, v in D.items():
            trs = [dict(x, R=x['res'], levk=100.0 * x['sd'] * (1.0 + x['c']) / x['px'], rmin=1.0 * x['sd'] * (1.0 + x['c'])) for x in v['trades']]
            P = dict(base=50.0, start=10000.0, cap=0.0, capAction='clamp', exitR=v['exitR'], ladT=1000.0)
            out[key] = dict(tf=v['tf'], idx=v['idx'], name=v['name'], exitR=v['exitR'], P=P, counts=trade_counts(trs), res=strategy_block(RC, trs, P), n=len(trs))
            w = out[key]['res']
            print('%-7s %-38s %5d trades | %s' % (key, v['name'], len(trs), ' '.join('%s/%s %+.0f' % (r_[-1], l[:2], w[(r_, l)]['whole']['net']) for r_, l in CONFIGS if l in ('Off', 'Max'))))
        pickle.dump(dict(months=MONTHS, configs=CONFIGS, strategies=out), open(S + '/mcej/ars_money.pkl', 'wb'))
    else:
        sys.path.insert(0, S + '/fractal')
        import recovery_tol as RC
        D = pickle.load(open(S + '/mcej/grid_trades.pkl', 'rb')); out = {}; TWIN_WORST = [0.0]
        for ctf in ('M5', 'M15'):
            ks = sorted(k for c, k in D if c == ctf); strat = {}
            for k in ks:
                v = D[(ctf, k)]; p = v['prm']
                P = dict(base=50.0, start=10000.0, cap=500.0, capAction='clamp', exitR=p[5] / p[4], ladT=1000.0)
                strat[k] = dict(prm=p, P=P, counts=trade_counts(v['trades']), res=strategy_block(RC, v['trades'], P), n=len(v['trades']), trades=v['trades'])
                # end-to-end check: the default setting (Crooks F + ladder Medium, $500 clamp) against the Pine twin's own money, trade by trade
                per = strat[k]['res'][('Crooks F', 'Medium')]['per']; tw = v['twin']['pnl']
                worst = max([abs(a[1] - b) / max(1.0, abs(b)) for a, b in zip(per, tw)] + [0.0])     # float noise only (the twin books units x price)
                assert len(per) == len(tw) and worst < 1e-6, (ctf, k, len(per), len(tw), worst)
                TWIN_WORST[0] = max(TWIN_WORST[0], worst)
            comb = {}
            for cfg in CONFIGS:
                cm, whole = combine([(strat[k]['trades'], strat[k]['res'][cfg]['per']) for k in ks], 10000.0)
                fr = {m: dict(net=sum(strat[k]['res'][cfg]['fresh'][m]['net'] for k in ks)) for m in MONTHS}
                comb[cfg] = dict(cont=cm, whole=whole, fresh=fr)
            cnt = {m: {f: sum(strat[k]['counts'][m][f] for k in ks) for f in ('n', 'w', 'l', 'nStart')} for m in MONTHS}
            out[ctf] = dict(strategies=strat, combined=comb, counts=cnt, ks=ks)
            print(ctf, 'strategies', ks, '| combined:', ' '.join('%s/%s %+.0f' % (r_[-1], l[:2], comb[(r_, l)]['whole']['net']) for r_, l in CONFIGS if l in ('Off', 'Medium', 'Max')))
            print('   twin check (Crooks F + Medium, every trade): OK for %d strategies, worst relative P&L difference so far %.1e' % (len(ks), TWIN_WORST[0]))
        for ctf in out:
            for k in out[ctf]['strategies']: out[ctf]['strategies'][k].pop('trades')
        pickle.dump(dict(months=MONTHS, configs=CONFIGS, charts=out), open(S + '/mcej/grid_money.pkl', 'wb'))
