"""v4.6 study round 3 = round 2 (house-money ladder v2) + a START GUARD: after the target, while the closed profit is at or
below the start (0), every trade is the 0.01 lot (g0) or half the plain risk (g1); round 2 text: (round 1 = crooks_ladder_v1_strictfloor.txt: a strict floor with trades clamped to a share of the cushion cut the profit
roughly in half and still went below the start in 20-50% of the shuffles, because 0.01-lot trades leak below the floor).
HOUSE MONEY ladder (v2): before the profit target T the rule trades as now. Once the highest closed profit has reached T:
  lock    L = lam x highest closed profit; cushion C = max(0, closed profit - L) = the profit that may be put at extra risk
  base    B = base + min((bmax - 1) x base, phi x C)     (the rule then works with B: waiting trades, caps, limits)
  limit   a trade risks at most what the rule risks at the plain base + gam x C: the extra risk is paid only from the cushion,
          and the ladder never risks less than the plain rule
v3 = v2 + safety mode: while the closed profit is below the lock (after T), every trade is 0.01 lot (or the plain base if smaller).
Output: crooks_ladder.pkl + crooks_ladder.txt."""
import sys, pickle, random, bisect
from multiprocessing import Pool
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks, greedy

LEV = 100.0
LEVELS = {'Low': dict(lam=0.8, phi=0.1, bmax=2.0, gam=0.25), 'Medium': dict(lam=0.7, phi=0.15, bmax=3.0, gam=0.3),
          'High': dict(lam=0.6, phi=0.2, bmax=5.0, gam=0.35), 'Extra high': dict(lam=0.5, phi=0.25, bmax=8.0, gam=0.4),
          'Max': dict(lam=0.4, phi=0.3, bmax=12.0, gam=0.5)}
MAPS = {'A': 1.0, 'slow': 0.5, 'fast': 1.5}
RULES = ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')


def lad_base(base, net, pk, L):
    """the ladder's base B, the cushion C and whether the profit is below the lock (None when the target is not reached yet)"""
    if L is None or pk < L['T']: return base, None, False
    C = net - L['lam'] * pk
    return base + min((L['bmax'] - 1.0) * base, L['phi'] * max(0.0, C)), max(0.0, C), C < 0


def rule_risk(rule, B, crL, won, exitR, eq, pk, net, rmin, fK, hPct, jX):
    rec = crL > 0 and won
    if rec:
        r = max(B, crL / exitR)
        if rule in ('Crooks F', 'Crooks I'): r = min(r, fK * B)
        elif rule == 'Crooks H': r = min(r, max(B, eq * hPct / 100.0))
        elif rule == 'Crooks J': r = max(B, r * max(0.0, 1.0 - max(0.0, pk - net) / (jX * B)))
    elif crL > 0 and rule in ('Crooks E', 'Crooks I'): r = min(B, rmin)
    else: r = B
    return r, rec


def sim(seq, exitR, rule, L=None, base=50.0, start=10000.0, fK=3.0, gX=10.0, hPct=1.0, jX=20.0):
    eq = start; peakEq = start; maxDD = maxDDp = net = 0.0; pk = 0.0; ruined = False; maxRisk = 0.0
    crL = 0.0; won = False; reached = False; minAfter = None; giveMax = 0.0; below0 = False; tReach = None
    for k, (t, res, c, sd, levk) in enumerate(seq):
        rmin = 1.0 * sd * (1.0 + c)                                       # 0.01 lot = 1 oz of gold at the stop, cost included
        B, C, below = lad_base(base, net, pk, L)
        r0, rec = rule_risk(rule, base, crL, won, exitR, eq, pk, net, rmin, fK, hPct, jX)
        if C is None: r = r0
        else:
            r1, _ = rule_risk(rule, B, crL, won, exitR, eq, pk, net, rmin, fK, hPct, jX)
            r = min(r1, r0 + L['gam'] * C)                                # the extra risk is paid only from the cushion
            if below and L.get('safe'): r = min(base, rmin)               # v3: below the lock, 0.01 lot
            if net <= 0 and L.get('guard') == 'g0': r = min(base, rmin)    # start guard: back at the start -> 0.01 lot
            elif net <= 0 and L.get('guard') == 'g1': r = 0.5 * r0          #   ... or half the plain risk
        r = min(r, eq * levk) if eq > 0 else r                            # 1:100 leverage
        r = max(r, rmin)                                                  # the 0.01-lot minimum
        pnl = r * (res - c) / (1.0 + c); maxRisk = max(maxRisk, r)
        eq += pnl; net += pnl
        peakEq = max(peakEq, eq); dd = peakEq - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peakEq)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        pk = max(pk, net)
        if rule == 'Crooks G': crL = min(crL, gX * lad_base(base, net, pk, L)[0])
        if crL < 0.01: crL = 0.0
        won = win
        if L is not None and pk >= L['T']:
            if not reached: reached = True; tReach = t
            minAfter = net if minAfter is None else min(minAfter, net)
            giveMax = max(giveMax, (pk - net) / pk if pk > 0 else 0.0)
            if net < 0: below0 = True
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, ruined=ruined, maxRisk=maxRisk, reached=reached, minAfter=minAfter, give=giveMax,
                below0=below0, tReach=tReach)


def price_lookup():
    d = pickle.load(open(S + '/gold/data/H1.pkl', 'rb'))
    return d['srv'], d['C']


def job(arg):
    tf, i = arg
    T_, Cl = price_lookup()
    d = crooks.sources(tf)[i]
    dd = dict(greedy.defaults()); dd.update(d['cfg'])
    if dd['exitAt'] > 1 and dd['p1']: return None
    xr = crooks.exit_r(d['cfg'])
    seq = []
    for x in sorted(d['trades'], key=lambda x: x[0]):
        j = max(0, bisect.bisect_right(T_, x[0]) - 1); px = Cl[j]; sd = x[5]; c = x[4] / x[5]
        seq.append((x[0], x[1], c, sd, LEV * sd * (1.0 + c) / px))
    if RC.simulate([(r_, c) for _, r_, c, _, _ in seq], 'Off', exitR=xr)['net'] <= 0: return None
    rng = random.Random(411 + i + 31 * crooks.TFS.index(tf)); times = [x[0] for x in seq]; outs = [x[1:] for x in seq]
    orders = []
    for _ in range(200):
        q = list(outs); rng.shuffle(q); orders.append([(t,) + o for t, o in zip(times, q)])
    ways = []
    for rule in RULES:
        ways.append((rule + ' (no ladder)', rule, None))
        for T in (500.0, 1000.0):
            ways.append(('%s | plain | target %d' % (rule, T), rule, dict(lam=0.0, phi=0.0, bmax=1.0, gam=0.0, T=T)))
            for g in ('g0', 'g1'): ways.append(('%s | plain %s | target %d' % (rule, g, T), rule, dict(lam=0.0, phi=0.0, bmax=1.0, gam=0.0, T=T, guard=g)))
            for lv, p in LEVELS.items():
                for g in (None, 'g0', 'g1'):
                    ways.append(('%s | v2%s %s | target %d' % (rule, '' if g is None else ' ' + g, lv, T), rule, dict(p, T=T, guard=g)))
    out = {}
    for nm, rule, L in ways:
        r = sim(seq, xr, rule, L); sims = [sim(q, xr, rule, L) for q in orders]
        out[nm] = dict(all=r, ruin=sum(z['ruined'] for z in sims) / len(sims), below0=sum(z['below0'] for z in sims) / len(sims),
                       reach=sum(z['reached'] for z in sims) / len(sims), med=sorted(z['net'] for z in sims)[100],
                       dd95=sorted(z['maxDDpct'] for z in sims)[189], give95=sorted(z['give'] for z in sims)[189],
                       minAfter5=sorted((z['minAfter'] if z['minAfter'] is not None else 0.0) for z in sims)[10])
    return '%s %s' % (tf, d['name']), out


if __name__ == '__main__':
    args = [(tf, i) for tf in crooks.TFS for i in range(len(crooks.sources(tf)))]
    with Pool(4) as pool: res = [r for r in pool.map(job, args) if r is not None]
    names = [n for n, _ in res]; rows = {}
    for _, out in res:
        for k, v in out.items(): rows.setdefault(k, []).append(v)
    pickle.dump(dict(rows=rows, names=names), open(S + '/gold/crooks_ladder3.pkl', 'wb'))
    L = ['%d strategies' % len(names), '']
    for nm, rs in rows.items():
        L.append('%-44s total %+10.0f | fall avg %5.1f%% worst %5.1f%% | blown %d | random: median %+10.0f, blown %5.1f%%, 95%% fall %5.1f%% | reached target %5.1f%% | after target: below start %5.2f%%, 95%% giveback %5.1f%% of the best profit, 5%% lowest profit %+8.0f' % (
            nm, sum(r['all']['net'] for r in rs), 100 * sum(r['all']['maxDDpct'] for r in rs) / len(rs), 100 * max(r['all']['maxDDpct'] for r in rs),
            sum(r['all']['ruined'] for r in rs), sum(r['med'] for r in rs), 100 * sum(r['ruin'] for r in rs) / len(rs), 100 * sum(r['dd95'] for r in rs) / len(rs),
            100 * sum(r['reach'] for r in rs) / len(rs), 100 * sum(r['below0'] for r in rs) / len(rs), 100 * sum(r['give95'] for r in rs) / len(rs),
            sum(r['minAfter5'] for r in rs) / len(rs)))
    open(S + '/gold/crooks_ladder3.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
