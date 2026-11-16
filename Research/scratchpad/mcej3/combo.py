"""50 / 50 combination of the two strategies: $500 in an Auction Retest setting and $500 in a grid setting (its strategies split the $500),
each month on its own; the month = the sum; the deepest drop inside the month on the summed balance (trades merged by exit time).
Output: mcej3/combo.pkl + combo.txt"""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mcej3'); sys.path.insert(0, S + '/gold')
import robust as RB, search as SE
import recovery as RC
D = RB.D
RULE = {r[0]: (r[1], r[2]) for r in SE.RULES}


def part_events(trs, exitR, kind, mode, kw, base, start, cap, act, lock):
    """per window: list of (exit time, pnl) of the trades taken (the lock stops new trades once the window's profit reaches it)"""
    out = []
    for items in RB.split_x(trs, kind, None):
        if not items: out.append([]); continue
        tup = [a for a, _ in items]; tr = []
        RC.simulate(tup, mode, base=base, start=start, cap=cap, capAction=act, exitR=exitR, trace=tr, **kw)
        ev = []; eq = 0.0
        for v, (t_, tx) in zip(tr, items):
            if lock is not None and eq >= lock: break
            p = v * (t_[0] - t_[1]) / (1.0 + t_[1]); eq += p; ev.append((tx, p))
            if start + eq <= 0: break
        out.append(ev)
    return out


def combo(ars, grid, kind):
    k, rule, base, cap, act, lock = ars
    s = [x for x in D['ars'] if x['key'] == k][0]; mode, kw = RULE[rule]
    E = part_events(s['trades'], s['exitR'], kind, mode, kw, base, 500.0, cap, act, lock)
    subset, grule, gbase, gcap, gact = grid; gm, gkw = RULE[grule]
    for g in subset:
        gs = D['grid'][g]
        for w, ev in enumerate(part_events(gs['trades'], gs['exitR'], kind, gm, gkw, gbase, 500.0 / len(subset), gcap, gact, None)): E[w] = E[w] + ev
    res = []
    for ev in E:
        eq = pk = dd = 0.0
        for _, p in sorted(ev, key=lambda z: z[0]):
            eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
        res.append((eq, dd))
    return res


def summary(res, kind):
    W = RB.WIN[kind]; o = {}
    for per in ('IN', 'OUT', None):
        v = [r for r, w in zip(res, W) if per is None or w[2] == per]
        n = [x[0] for x in v]
        o[per or 'ALL'] = dict(prof=sum(1 for x in n if x > 1e-9), lose=sum(1 for x in n if x < -1e-9), total=sum(n), worst=min(n), dd=max(x[1] for x in v))
    return o


if __name__ == '__main__':
    CASES = {'safe + balanced': (('M15-S3 fcOff', "Oscar's Grind", 5.0, 0.0, 'clamp', 10.0), ((6, 7, 9), 'Exact recovery at final TP', 5.0, 50.0, 'clamp')),
             'no recovery + balanced': (('M15-S3 fcOff', 'No recovery', 10.0, 0.0, 'clamp', 10.0), ((6, 7, 9), 'Exact recovery at final TP', 5.0, 50.0, 'clamp')),
             'safe + safe': (('M15-S3 fcOff', "Oscar's Grind", 5.0, 0.0, 'clamp', 10.0), ((0, 1, 5, 6, 7, 9), 'Exact recovery at final TP', 2.5, 25.0, 'clamp'))}
    out = {}; L = []
    for nm, (a, g) in CASES.items():
        r = {kind: combo(a, g, kind) for kind in ('cal', 'mid')}
        sm = {kind: summary(r[kind], kind) for kind in r}
        out[nm] = dict(ars=a, grid=g, monthly=[x[0] for x in r['cal']], dd=[x[1] for x in r['cal']], sum=sm)
        c, m = sm['cal'], sm['mid']
        L.append('%-24s ARS %s | GRID %s\n   all 70 months: %d profit / %d loss, %+.0f, worst %+.0f, deepest drop %.0f | choice 2021-23: %d loss %+.0f | test 2024-26: %d loss %+.0f worst %+.0f | mid-month: %d loss, worst %+.0f' % (
            nm, a, ('+'.join('S%d' % (x + 1) for x in g[0]),) + g[1:], c['ALL']['prof'], c['ALL']['lose'], c['ALL']['total'], c['ALL']['worst'], c['ALL']['dd'],
            c['IN']['lose'], c['IN']['total'], c['OUT']['lose'], c['OUT']['total'], c['OUT']['worst'], m['ALL']['lose'], m['ALL']['worst']))
    pickle.dump(out, open(S + '/mcej3/combo.pkl', 'wb')); open(S + '/mcej3/combo.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
