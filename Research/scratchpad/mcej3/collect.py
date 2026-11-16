"""Best monthly settings with a fresh $1,000 every month (asked 2026-11-16): the trade sets.
Auction Retest (ARS): every catalogue strategy without a partial close (as designed, kill zones following summer time like the strategy's
  default) and the user's settings (M5 / M15 / H1, filters off / on, final exit TP1..TP4), each through the TradingView strategy model
  (mcej2/ref_gse.py events + mcej2/stratemu.py: earn-back targets, costs 0.23 per oz, close at Saturday start; force-close 23:55 on, and for
  the catalogue also off; the daily news window only with the user's filters).
Grid: the 12 Fractal Breakout Grid strategies on the M1 model (= the grid EA and a TradingView M1 chart), costs 0.23.
Per trade: entry / exit time (IST), R, cost in R, stop distance, leverage limit per $, 0.01-lot $ risk. Output: mcej3/sets.pkl"""
import sys, pickle, multiprocessing as mp, datetime as dt
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build'); sys.path.insert(0, S + '/mcej2')
COST = 0.23
USER_ENG = dict(halfCap=True, maxFills=10, entryPct=25.0, mv3R=0.0, noChaseSig=2.0, chopMax=13.5, kzShift=0, kzAuto=True)
USER_SETUP = {'off': (dict(dayOn=False, hoursOn=False, kzOn=False), False),
              'on': (dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300), kzOn=True,
                          kz=(True, True, True, False)), True)}


def ars_sets():
    import crooks, greedy
    out = []
    for tf in ('M1', 'M5', 'M15', 'H1'):
        for i, d in enumerate(crooks.sources(tf)):
            if i == 0: continue                                   # the old v3 defaults (lose at a fixed risk)
            dd = dict(greedy.defaults()); dd.update(d['cfg'])
            if dd['exitAt'] > 1 and dd.get('p1'): continue         # partial close at TP1: not in the strategy model
            for fc in (True, False):
                out.append(dict(key='%s-S%d%s' % (tf, i, '' if fc else ' fcOff'), fam='ARS', kind='catalogue', tf=tf, name=d['name'], cfg=dict(d['cfg']),
                                news=False, fc=fc, exitR=crooks.exit_r(d['cfg'])))
    for tf in ('M5', 'M15', 'H1'):
        for su in ('off', 'on'):
            for ex in (1, 2, 3, 4):
                out.append(dict(key='%s-you-%s-TP%d' % (tf, su, ex), fam='ARS', kind='your settings', tf=tf,
                                name='your settings, %s, exit TP%d' % ('all filters off' if su == 'off' else 'your filters', ex),
                                cfg=dict(USER_ENG, exitAt=ex, **USER_SETUP[su][0]), news=USER_SETUP[su][1], fc=True, exitR=(0.6, 1.0, 1.5, 2.0)[ex - 1]))
    return out


def ars_job(s):
    import geng, ref_gse, stratemu as EM
    ref_gse.eprep = geng.ref_g.eprep
    o = {k: v for k, v in s['cfg'].items() if k != 'p1'}
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    if o.get('kzOn'): o['kzAuto'] = True                          # the strategy's default (kill zones follow summer time)
    P = geng.prepare(s['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    ev = []; eng = ref_gse.run(s['tf'], o, ev)
    fl = EM.time_flags(P['T'], fcOn=s['fc'], wkOn=True, newsOn=s['news'])
    tr, cnt = EM.run(P['O'], P['H'], P['L'], P['C'], P['T'], ev, P['mt'], earnBack=True, costPx=COST, flags=fl, market=o.get('entryMode') == 'market')
    out = []
    for x in tr:
        if x['exit'] is None: continue
        d = x['dir']; rp = x['risk']
        out.append(dict(t=P['T'][x['fill']], tx=P['T'][x['exit']], R=d * (x['xpx'] - x['fpx']) / rp, c=COST / rp, sd=rp,
                        levk=100.0 * (rp + COST) / x['lim'], rmin=rp + COST, how=x['how']))
    # check: with earn-back and the time closes off the model must take the engine's trades
    tr0, _ = EM.run(P['O'], P['H'], P['L'], P['C'], P['T'], ev, P['mt'], earnBack=False, flags=EM.time_flags(P['T'], fcOn=False, wkOn=False), market=o.get('entryMode') == 'market')
    A0 = {(x['dir'], x['fill'], x['exit']) for x in eng if not x['ghost'] and x['exit'] is not None}; B0 = {(x['dir'], x['fill'], x['exit']) for x in tr0 if x['exit'] is not None}
    return dict(s, trades=out, engine=len([x for x in eng if not x['ghost']]), cnt=cnt, check=(len(A0), len(B0), len(A0 & B0)))


def grid_sets():
    sys.path.insert(0, S + '/fractal')
    import engine as EN
    from final11 import ALL12
    B = EN.load()
    for k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + k] = B[k]
    IST = ZoneInfo('Asia/Kolkata'); utc = B['ut']; out = []
    for k, p in enumerate(ALL12, 1):
        tr = EN.run(B, 'M1', *p); sl, tp = p[4], p[5]; L = []
        for x in tr:
            e, F, xb, X = int(x[0]), float(x[1]), int(x[2]), float(x[3]); sd = F * sl / 100.0
            L.append(dict(t=dt.datetime.fromtimestamp(int(utc[e]), IST).replace(tzinfo=None), tx=dt.datetime.fromtimestamp(int(utc[xb]), IST).replace(tzinfo=None),
                          R=(X - F) / sd, c=COST / sd, sd=sd, levk=100.0 * (sd + COST) / F, rmin=sd + COST))
        out.append(dict(key='S%d' % k, fam='GRID', kind='grid strategy', tf=p[0], name='S%d %s R%d/L%d off %+.3f%% SL %.2f%% TP %.2f%% BE %.2f%% salvage %.2f%%' % (
            k, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]), prm=p, exitR=tp / sl, trades=L))
    return out


if __name__ == '__main__':
    A = ars_sets()
    order = sorted(A, key=lambda s: {'M1': 0, 'H1': 3, 'M5': 1, 'M15': 2}[s['tf']])          # the slow M1 runs first
    with mp.Pool(4) as pool: R = pool.map(ars_job, order, chunksize=1)
    pickle.dump(dict(ars=R), open(S + '/mcej3/sets_ars.pkl', 'wb'))
    with mp.get_context('spawn').Pool(1) as pool: G = pool.apply(grid_sets)      # a fresh interpreter: fractal/engine.py, not another engine.py
    pickle.dump(dict(ars=R, grid=G), open(S + '/mcej3/sets.pkl', 'wb'))
    for r in R:
        tr = r['trades']; net = sum((x['R'] - x['c']) / (1 + x['c']) for x in tr)
        print('%-26s %5d trades (engine %5d) net %+8.1fR at a fixed risk | exitR %.2f | check engine %d model %d same %d' % (r['key'], len(tr), r['engine'], net, r['exitR'], *r['check']))
    for g in G:
        tr = g['trades']; print('%-5s %5d trades net %+7.1fR' % (g['key'], len(tr), sum((x['R'] - x['c']) / (1 + x['c']) for x in tr)))
